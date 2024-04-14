class MODEL_CONFIG:
  __conf = {
    "TEST_CASE_SYSTEM": "Review the shared code context to identify the {language} testing framework and libraries in use. Then, create multiple new unit tests for the test suite in my selected code following the same patterns, testing conventions, and testing library as shown in the shared context. Pay attention to the shared context to ensure that your response code does not contain cases that have already been covered. Focus on generating new unit tests for uncovered cases. Respond only with the fully completed code with the new unit tests added at the end, without any comments, fragments, or TODO. The new tests should validate expected functionality and cover edge cases for the test suites. The goal is to provide me with code that I can add to the end of the existing test file. Do not repeat tests from the shared context. Enclose only the new tests without describe/suite, import statements, or packages in your response.",
    "AUTOCOMPLETE_CODE_SYSTEM": "Review the shared code context to identify the {language} framework and just write the next lines of code without explanation about it.",
    "TEST_CASE_SYSTEM_MAX_TOKENS": 1024,
    "AUTOCOMPLETE_CODE_SYSTEM_MAX_TOKENS": 124,
    "EXPLAIN_CODE": "Explain what the selected code does in simple terms for the {language} language. Assume the audience is a beginner programmer who has just learned the language features and basic syntax. Focus on explaining: 1) The purpose of the code 2) What input(s) it takes 3) What output(s) it produces 4) How it achieves its purpose through the logic and algorithm. 5) Any important logic flows or data transformations happening. Use simple language a beginner could understand. Include enough detail to give a full picture of what the code aims to accomplish without getting too technical. Format the explanation in coherent paragraphs, using proper punctuation and grammar. Write the explanation assuming no prior context about the code is known. Do not make assumptions about variables or functions not shown in the shared code. Start the answer with the name of the code that is being explained.",
    "EXPLAIN_CODE_SYSTEM_MAX_TOKENS": 1024
  }
  # Reference: https://stackoverflow.com/questions/6198372/most-pythonic-way-to-provide-global-configuration-variables-in-config-py
  #__setters = ["username", "password"]

  @staticmethod
  def config(name):
    return MODEL_CONFIG.__conf[name]

  @staticmethod
  def set(name, value):
    if name in MODEL_CONFIG.__setters:
      MODEL_CONFIG.__conf[name] = value
    else:
      raise NameError("Name not accepted in set() method")