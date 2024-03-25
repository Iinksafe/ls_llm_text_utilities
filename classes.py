from binascii import crc32
from requests import post
from types import *


# Section: API & Authentication. Variables
api_url: str = 'https://api.aichatting.net/aigc/chat'
api_headers: dict[str, str] = {}


def _crc32(data: bytes, crc: int = 0, /): return crc32(data, crc)
def _sum(data: bytes, z: int = 0, /): return sum(x * y + z for x, y in enumerate(data, z + 1))

class GenerationError(Exception):
  """There was an error generating
  the text. Try again in a few
  minutes."""
  pass


class AI():
    history = NotImplemented

    def __init__(self) -> None:
      self.history: list[str] = []

    def instruct(self, instruction: str) -> None:
      """Append a system instruction to the LLM."""
      self.history.append(f'[system] {instruction}')

    def respond(self, text: str) -> str:
        self.history.append(f'[user] {text}')
      
        response = post(api_url, headers=api_headers, json={'content': content})
      
        try:
          response = response.json()['data']['replyContent']
        except:
          raise GenerationError(response.text)
          
        self.history.append(f'[assistant] {response}')
        return response


class LLM():
  def __getattribute__(self, name: str) -> FunctionType:
      ai: AI = AI()
      TYPE: type = type
      OK: Literal['OK'] = 'OK'
      safe: dict[str, dict] = {'__builtins__': {}}
      def value(*a: Any, type: str, format: str = '', **b: dict[str, Any]) -> tuple[Literal[0], str] | tuple[Literal[1] | Literal[2], Any] | tuple[Literal[3] | Literal[4], str]:
          """Query a response from the LLM with the given arguments. The return type can be specified by the `type` parameter and its format can be aligned setting `format`."""
    
          if format: b['return_format'] = format

          ai.history.clear()

          HEAD: str = ''
          if a: HEAD += ',\x20'.join(f'_{z}:\x20' + TYPE(arg).__name__ for z, arg in enumerate(a))
          if b: HEAD += (',\x20' if a else '') + '*,\x20' + ',\x20'.join(f'{x}:\x20{TYPE(y).__name__}' for x, y in b.items())
          HEAD = f'def {name}({HEAD}) -> {type}: [native code]'

          ai.instruct(f'You are a Python code interpreter. Only respond with code output in verbatim. If you cannot do something, format it like a Python exception.')
          ai.instruct(f"Replace '[native code]' with the desired function body, and only return '{OK}|' + the function's output in verbatim.")

          BODY: str = ''
          if a: BODY += ',\x20'.join(repr(arg) if str == TYPE(arg) else str(arg) for arg in a)
          if b: BODY += (',\x20' if a else '') + ',\x20'.join(f'{x}={repr(y) if str == TYPE(y) else y}' for x, y in b.items())
          arguments: str = HEAD + '\n' + 'print(' + name + '(' + BODY + 2 * ')'
          ok_response: list[str] = ai.respond(arguments).split('|', 1)

          try: ok: str, response: str = ok_response
          except ValueError: return 0, ok_response[0]

          Ok = ok == OK

          try: return 1 + Ok, eval(response, safe, safe)
          except: return 3 + Ok, response
      value.__name__ = name
      return value

class Cipher():
  def __init__(self, password: bytes = b'', *, salt: int = 0x00) -> None:
    self.password = password
    self.salt = salt
    
  def encrypt(msg: bytes, /, **options) -> str:
      msg = msg.hex().encode()
    
      password = self.password
      salt = self.salt
    
      if not password: password = msg
  
      password = str(salt).join(str(_sum(password, salt) + _crc32(password, salt)).join(password.decode())).encode()
  
      msg_len = len(msg)
  
      if len(password) < msg_len:
          password *= msg_len
          password = password[:msg_len]
  
      # just in case the password is empty or there was an error
      assert msg_len <= len(password), 'message is too long'
  
      msg_len = str(msg_len).encode()
  
      message = msg.zfill(len(password))
      int_password = int.from_bytes(password, **options)
      int_message = int.from_bytes(message, **options)
  
      bytes = str(_sum(msg_len, salt) + _crc32(msg_len, salt)).encode() + b'\x00' + int.to_bytes(int_message + int_password, len(message), **options)
      return bytes.hex()
  
  def decrypt(hex: str, /, **options) -> bytes:
      raw_digest, message = bytes.fromhex(hex).split(b'\x00', 1)
      digest_detected, digest = False, int(raw_digest)

      password = self.password
      salt = self.salt
    
      for _msg_len in range(len(hex)):
          msg_len = str(_msg_len).encode()
          if digest == f(msg_len, salt) + ff(msg_len, salt):
              digest_detected = True
              digest = _msg_len
              break
  
      assert digest_detected, 'invalid salt'
  
      password = str(salt).join(str(_sum(password, salt) + _crc32(password, salt)).join(password.decode())).encode()
  
      msg_len = len(message)
  
      if len(password) < msg_len:
          password *= msg_len
          password = password[:msg_len]
  
      int_message = int.from_bytes(message, **options)
      int_password = int.from_bytes(password, **options)
  
      try: return bytes.fromhex(int.to_bytes(int_message - int_password, msg_len, **options)[len(password) - digest:].decode())
      #except OverflowError: raise TypeError('invalid password') from None
      except ValueError: raise TypeError('invalid password') from None
