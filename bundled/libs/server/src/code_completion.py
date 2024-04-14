from pygls.server import LanguageServer
import logging
from lsprotocol.types import (
    # TEXT_DOCUMENT_INLINE_COMPLETION,
    # InlineCompletionOptions,
    # InlineCompletionParams,
    # InlineCompletionTriggerKind,
    # InlineCompletionList,
    # InlineCompletionItem
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions,
    CompletionParams,
    CompletionTriggerKind,
    CompletionList,
    CompletionItem,
)
from compute_model import LoadModel,ComputeModelInformation
from computeInterface import ComputeData
from config import MODEL_CONFIG

server = LanguageServer("code-completion", "v0.1")
# Create and configure logger
logging.basicConfig(filename="newfile_completion.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

'''
 @ls.feature('textDocument/completion', CompletionOptions(trigger_characters=['.']))
   def completions(ls, params: CompletionParams):
       return CompletionList(is_incomplete=False, items=[CompletionItem("Completion 1")])
'''
@server.feature(
TEXT_DOCUMENT_COMPLETION,
CompletionOptions(trigger_characters=['.'])
)
def Completions(params: CompletionParams):
    logger.debug("Entered Completion function!")
    return CompletionList(is_incomplete=False, items=[CompletionItem("Completion 1")])


@server.command(
    'codesculptor.server.generateTestCase'
)
def GenerateTestCase(ls, *args):
    logger.debug("called test case function")
    reqData = args[0]
    logger.debug(f"Arguments of ReqData: ${reqData[0]}")
    data = ComputeData(reqData[0]["text"], MODEL_CONFIG.config("TEST_CASE_SYSTEM").replace("{language}", reqData[0]["language"]),True, MODEL_CONFIG.config("TEST_CASE_SYSTEM_MAX_TOKENS"))
    testCase = ComputeModelInformation(data)
    logger.debug(testCase)
    return testCase

@server.command(
    'codesculptor.server.suggestCode'
)
def SuggestCode(ls, *args):
    logger.debug("called suggest code function")
    reqData = args[0]
    logger.debug(f"Arguments of ReqData: ${reqData[0]}")
    data = ComputeData(reqData[0]["text"], MODEL_CONFIG.config("AUTOCOMPLETE_CODE_SYSTEM").replace("{language}", reqData[0]["language"]),True, MODEL_CONFIG.config("AUTOCOMPLETE_CODE_SYSTEM_MAX_TOKENS"))
    codeSuggestion = ComputeModelInformation(data)
    logger.debug(codeSuggestion)
    return codeSuggestion

#@server.thread()
@server.command(
    'codesculptor.server.initializeModel'
)
def Initialize(ls, *args):
    LoadModel()
    logger.debug("Model initialized")
    return "Model initialized"

if __name__ == "__main__":
    server.start_io()