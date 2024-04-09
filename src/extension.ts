// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as net from "net";
import * as path from "path";
import * as vscode from "vscode";
import * as semver from "semver";

import { PythonExtension } from "@vscode/python-extension";
import { LanguageClient, LanguageClientOptions, ServerOptions, State, TransportKind, integer } from "vscode-languageclient/node";

const MIN_PYTHON = semver.parse("3.7.9")!;

let client: LanguageClient;
let clientStarting = false;
let python: PythonExtension
let logger: vscode.LogOutputChannel

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export async function activate(context: vscode.ExtensionContext) {
    logger = vscode.window.createOutputChannel('Code Sculptor', { log: true })
    logger.info("Extension activated.")

    vscode.window.showInformationMessage("Code Sculptor activated!")
    await getPythonExtension();
    if (!python) {
        return
    }

    // Restart language server command
    context.subscriptions.push(
        vscode.commands.registerCommand("codesculptor.server.restart", async () => {
            logger.info('restarting server...')
            await startLangServer()
        })
    )

    // Execute command... command
    context.subscriptions.push(
        vscode.commands.registerCommand("codesculptor.server.executeCommand", async () => {
            await executeServerCommand()
        })
    )

    // Generate Unit Test case
    context.subscriptions.push(
        vscode.commands.registerCommand("codesculptor.generateTestCase", async () => {
            await generateUnitTestCase()
        })
    )

    // Restart the language server if the user switches Python envs...
    context.subscriptions.push(
        python.environments.onDidChangeActiveEnvironmentPath(async () => {
            logger.info('python env modified, restarting server...')
            await startLangServer()
        })
    )

    // ... or if they change a relevant config option
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(async (event) => {
            if (event.affectsConfiguration("codesculptor.server") || event.affectsConfiguration("codesculptor.client")) {
                logger.info('config modified, restarting server...')
                await startLangServer()
            }
        })
    )

    // Start the language server once the user opens the first text document...
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(
            async () => {
                if (!client) {
                    await startLangServer()
                }
            }
        )
    )

    // ...or notebook.
    context.subscriptions.push(
        vscode.workspace.onDidOpenNotebookDocument(
            async () => {
                if (!client) {
                    await startLangServer()
                }
            }
        )
    )

    // Restart the server if the user modifies it.
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document: vscode.TextDocument) => {
            const expectedUri = vscode.Uri.file(path.join(getCwd(), getServerPath()))

            if (expectedUri.toString() === document.uri.toString()) {
                logger.info('server modified, restarting...')
                await startLangServer()
            }
        })
    )

    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider('plaintext', {
            provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {

                // a simple completion item which inserts `Hello World!`
                const simpleCompletion = new vscode.CompletionItem('Hello World!');

                // a completion item that inserts its text as snippet,
                // the `insertText`-property is a `SnippetString` which will be
                // honored by the editor.
                const snippetCompletion = new vscode.CompletionItem('Good part of the day');
                snippetCompletion.insertText = new vscode.SnippetString('Good ${1|morning,afternoon,evening|}. It is ${1}, right?');
                const docs: any = new vscode.MarkdownString("Inserts a snippet that lets you select [link](x.ts).");
                snippetCompletion.documentation = docs;
                docs.baseUri = vscode.Uri.parse('http://example.com/a/b/c/');

                // a completion item that can be accepted by a commit character,
                // the `commitCharacters`-property is set which means that the completion will
                // be inserted and then the character will be typed.
                const commitCharacterCompletion = new vscode.CompletionItem('console');
                commitCharacterCompletion.commitCharacters = ['.'];
                commitCharacterCompletion.documentation = new vscode.MarkdownString('Press `.` to get `console.`');

                // a completion item that retriggers IntelliSense when being accepted,
                // the `command`-property is set which the editor will execute after 
                // completion has been inserted. Also, the `insertText` is set so that 
                // a space is inserted after `new`
                const commandCompletion = new vscode.CompletionItem('new');
                commandCompletion.kind = vscode.CompletionItemKind.Keyword;
                commandCompletion.insertText = 'new ';
                commandCompletion.command = { command: 'editor.action.triggerSuggest', title: 'Re-trigger completions...' };

                // return all completion items as array
                return [
                    simpleCompletion,
                    snippetCompletion,
                    commitCharacterCompletion,
                    commandCompletion
                ];
            }
        })
    )

    context.subscriptions.push(
        vscode.languages.registerInlineCompletionItemProvider('plaintext', {
            provideInlineCompletionItems(document: vscode.TextDocument, position: vscode.Position, context: vscode.InlineCompletionContext, token: vscode.CancellationToken) {
                //provideInlineCompletionItems(document, position, context, token) {
                const inlineCommand = new vscode.InlineCompletionItem("test command when triggered")

                // return all completion items as array
                return [
                    inlineCommand
                ];
            }
        })
    )

    context.subscriptions.push(vscode.commands.registerCommand('codesculptor.startTask', () => {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Loading Model!",
            cancellable: true
        }, async (progress, token) => {
            token.onCancellationRequested(() => {
                console.log("User canceled the long running operation");
            });

            progress.report({ increment: 30 });

            const p = new Promise<void>(async (resolve) => {
                if (!client || client.state !== State.Running) {
                    await vscode.window.showErrorMessage("There is no language server running.")
                    return
                }
                const result = await vscode.commands.executeCommand("initializeModel")
                return resolve()
            });

            return p;
        });
    }));
}

// This method is called when your extension is deactivated
export function deactivate(): Thenable<void> {
    return stopLangServer()
}

/**
 * Start (or restart) the language server.
 *
 * @param command The executable to run
 * @param args Arguments to pass to the executable
 * @param cwd The working directory in which to run the executable
 * @returns
 */
async function startLangServer() {

    // Don't interfere if we are already in the process of launching the server.
    if (clientStarting) {
        return
    }

    clientStarting = true
    if (client) {
        await stopLangServer()
    }
    const config = vscode.workspace.getConfiguration("codesculptor.server")
    const cwd = getCwd()
    const serverPath = getServerPath()

    logger.info(`cwd: '${cwd}'`)
    logger.info(`server: '${serverPath}'`)

    const resource = vscode.Uri.joinPath(vscode.Uri.file(cwd), serverPath)
    const pythonCommand = await getPythonCommand(resource)
    if (!pythonCommand) {
        clientStarting = false
        return
    }

    logger.debug(`python: ${pythonCommand.join(" ")}`)
    const serverOptions: ServerOptions = {
        command: pythonCommand[0],
        args: [...pythonCommand.slice(1), serverPath],
        options: { cwd },
        debug: {
            command: pythonCommand[0],
            args: [...pythonCommand.slice(1), serverPath],
            options: { cwd },
            transport: TransportKind.stdio
        }
    };

    client = new LanguageClient('codesculptor', serverOptions, getClientOptions());
    const promises = [client.start()]

    if (config.get<boolean>("debug")) {
        promises.push(startDebugging())
    }

    const results = await Promise.allSettled(promises)
    clientStarting = false

    for (const result of results) {
        if (result.status === "rejected") {
            logger.error(`There was a error starting the server: ${result.reason}`)
        }
    }
    vscode.commands.executeCommand('codesculptor.startTask')
}

async function stopLangServer(): Promise<void> {
    if (!client) {
        return
    }

    if (client.state === State.Running) {
        await client.stop()
    }

    client.dispose()
    //client = undefined   //TODO: Error on assigning Undefined
}



function startDebugging(): Promise<void> {
    if (!vscode.workspace.workspaceFolders) {
        logger.error("Unable to start debugging, there is no workspace.")
        return Promise.reject("Unable to start debugging, there is no workspace.")
    }
    // TODO: Is there a more reliable way to ensure the debug adapter is ready?
    setTimeout(async () => {
        // @ts-expect-error
        await vscode.debug.startDebugging(vscode.workspace.workspaceFolders[0], "codesculptor: Debug Server")
    }, 2000)
    return Promise.resolve();
}

function getClientOptions(): LanguageClientOptions {
    const config = vscode.workspace.getConfiguration('codesculptor.client')
    const options = {
        documentSelector: config.get<any>('documentSelector'),
        outputChannel: logger,
        connectionOptions: {
            maxRestartCount: 0 // don't restart on server failure.
        },
    };
    logger.info(`client options: ${JSON.stringify(options, undefined, 2)}`)
    return options
}


/**
 * Execute a command provided by the language server.
 */
async function executeServerCommand() {
    if (!client || client.state !== State.Running) {
        await vscode.window.showErrorMessage("There is no language server running.")
        return
    }

    const knownCommands = client.initializeResult?.capabilities.executeCommandProvider?.commands
    if (!knownCommands || knownCommands.length === 0) {
        const info = client.initializeResult?.serverInfo
        const name = info?.name || "Server"
        const version = info?.version || ""

        await vscode.window.showInformationMessage(`${name} ${version} does not implement any commands.`)
        return
    }

    const commandName = await vscode.window.showQuickPick(knownCommands, { canPickMany: false })
    if (!commandName) {
        return
    }
    logger.info(`executing command: '${commandName}'`)

    const result = await vscode.commands.executeCommand(commandName /* if your command accepts arguments you can pass them here */)
    logger.info(`${commandName} result: ${JSON.stringify(result, undefined, 2)}`)
}

async function generateUnitTestCase() {
    if (!client || client.state !== State.Running) {
        await vscode.window.showErrorMessage("There is no language server running.")
        return
    }

    const editor = vscode.window.activeTextEditor;
    const selection = editor?.selection;
    if (selection && !selection.isEmpty) {
        const selectionRange = new vscode.Range(selection.start.line, selection.start.character, selection.end.line, selection.end.character);
        const highlighted = editor.document.getText(selectionRange);
        logger.info(highlighted)

        // Generate test case for selected text
        const inputData:unknown = { text: highlighted, isSelection: true, language: 'python' }
        const result = await vscode.commands.executeCommand("generateTestCase", inputData)
        logger.info(JSON.stringify(result, undefined, 2))
    } else {

        const result = await vscode.commands.executeCommand("generateTestCase", { text: editor?.document.fileName, isSelection: false, language: 'python' })
        logger.info(`codesculptor.generateTestCase result: ${JSON.stringify(result, undefined, 2)}`)
    }
}

function getCwd(): string {
    const config = vscode.workspace.getConfiguration("codesculptor.server")
    const cwd = config.get<string>('cwd')
    if (cwd) {
        return cwd
    }

    const serverDir = path.resolve(
        path.join(__dirname, "..", "bundled/libs/server/src")   //TODO: Update the Path to the server file
    )
    return serverDir
}

/**
 *
 * @returns The python script that implements the server.
 */
function getServerPath(): string {
    const config = vscode.workspace.getConfiguration("codesculptor.server")
    const server = config.get<string>('launchScript')!
    return server
}

async function getPythonExtension() {
    try {
        python = await PythonExtension.api();
    } catch (err) {
        logger.error(`Unable to load python extension: ${err}`)
    }
}


async function getPythonCommand(resource?: vscode.Uri): Promise<string[] | undefined> {
    const config = vscode.workspace.getConfiguration("codesculptor.server", resource)
    const pythonPath = await getPythonInterpreter(resource)
    if (!pythonPath) {
        return
    }
    const command = [pythonPath]
    const enableDebugger = config.get<boolean>('debug')

    if (!enableDebugger) {
        return command
    }

    const debugHost = config.get<string>('debugHost')!
    const debugPort = config.get<integer>('debugPort')!
    try {
        const debugArgs = await python.debug.getRemoteLauncherCommand(debugHost, debugPort, true)
        // Debugpy recommends we disable frozen modules
        command.push("-Xfrozen_modules=off", ...debugArgs)
    } catch (err) {
        logger.error(`Unable to get debugger command: ${err}`)
        logger.error("Debugger will not be available.")
    }

    return command
}

/**
 * Return the python interpreter to use when starting the server.
 *
 * This uses the official python extension to grab the user's currently
 * configured environment.
 *
 * @returns The python interpreter to use to launch the server
 */
async function getPythonInterpreter(resource?: vscode.Uri): Promise<string | undefined> {
    const config = vscode.workspace.getConfiguration("codesculptor.server", resource)
    const pythonPath = config.get<string>('pythonPath')
    if (pythonPath) {
        logger.info(`Using user configured python environment: '${pythonPath}'`)
        return pythonPath
    }

    if (!python) {
        return
    }

    if (resource) {
        logger.info(`Looking for environment in which to execute: '${resource.toString()}'`)
    }
    // Use whichever python interpreter the user has configured.
    const activeEnvPath = python.environments.getActiveEnvironmentPath(resource)
    logger.info(`Found environment: ${activeEnvPath.id}: ${activeEnvPath.path}`)

    const activeEnv = await python.environments.resolveEnvironment(activeEnvPath)
    if (!activeEnv) {
        logger.error(`Unable to resolve envrionment: ${activeEnvPath}`)
        return
    }

    const v = activeEnv.version!
    const pythonVersion = semver.parse(`${v.major}.${v.minor}.${v.micro}`)!

    // Check to see if the environment satisfies the min Python version.
    if (semver.lt(pythonVersion, MIN_PYTHON)) {
        const message = [
            `Your currently configured environment provides Python v${pythonVersion} `,
            `but codesculptor requires v${MIN_PYTHON}.\n\nPlease choose another environment.`
        ].join('')

        const response = await vscode.window.showErrorMessage(message, "Change Environment")
        if (!response) {
            return
        } else {
            await vscode.commands.executeCommand('python.setInterpreter')
            return
        }
    }

    const pythonUri = activeEnv.executable.uri
    if (!pythonUri) {
        logger.error(`URI of Python executable is undefined!`)
        return
    }

    return pythonUri.fsPath
}