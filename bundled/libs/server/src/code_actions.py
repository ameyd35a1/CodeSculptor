import re
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_ACTION,
    CodeAction,
    CodeActionKind,
    CodeActionOptions,
    CodeActionParams,
    Position,
    Range,
    TextEdit,
    WorkspaceEdit,
)


ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=(?=\s*$)")
server = LanguageServer("code-action-server", "v0.1")


@server.feature(
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionOptions(code_action_kinds=[CodeActionKind.RefactorInline]),
)
def code_actions(params: CodeActionParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    for idx, line in enumerate(lines):
        match = ADDITION.match(line)
        if match is not None:
            range_ = Range(
                start=Position(line=start_line + idx, character=0),
                end=Position(line=start_line + idx, character=len(line) - 1),
            )

            left = int(match.group(1))
            right = int(match.group(2))
            answer = left + right

            text_edit = TextEdit(range=range_, new_text=f"{line.strip()} {answer}!")

            action = CodeAction(
                title=f"*Evaluate '{match.group(0)}'",
                kind=CodeActionKind.QuickFix,
                edit=WorkspaceEdit(changes={document_uri: [text_edit]}),
            )
            items.append(action)

    return items


if __name__ == "__main__":
    server.start_io()