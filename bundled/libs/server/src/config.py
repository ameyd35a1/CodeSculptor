class MODEL_CONFIG:
  __conf = {
    "TEST_CASE_SYSTEM": "Review the shared code context to identify the {language} testing framework and libraries in use. Then, create multiple new unit tests for the test suite in my selected code following the same patterns, testing conventions, and testing library as shown in the shared context. Pay attention to the shared context to ensure that your response code does not contain cases that have already been covered. Focus on generating new unit tests for uncovered cases. Respond only with the fully completed code with the new unit tests added at the end, without any comments, fragments, or TODO. The new tests should validate expected functionality and cover edge cases for the test suites. The goal is to provide me with code that I can add to the end of the existing test file. Do not repeat tests from the shared context. Enclose only the new tests without describe/suite, import statements, or packages in your response.",
    "AUTOCOMPLETE_CODE_SYSTEM": "Review the shared code context to identify the {language} framework and just write the next lines of code without explanation about it.",
    "TEST_CASE_SYSTEM_MAX_TOKENS": 1024,
    "AUTOCOMPLETE_CODE_SYSTEM_MAX_TOKENS": 124,
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