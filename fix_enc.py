
path = r'c:\Users\gromd\OneDrive\Документи\GitHub\Calogram\home.html'
with open(path, 'rb') as f:
    raw = f.read()
if raw[:3] == b'\xef\xbb\xbf':
    raw = raw[3:]
text = raw.decode('utf-8')

# The garbled text "Вітаємо" should be present
# Strategy: decode raw bytes as latin-1, then encode back to bytes, decode as utf-8
raw_as_latin1_chars = raw.decode('latin-1')
back_to_bytes = raw_as_latin1_chars.encode('latin-1')
result = back_to_bytes.decode('utf-8')

idx2 = result.find('Вітаємо')
print('Found Вітаємо at:', idx2)
print('Sample:', result[idx2-20:idx2+60])
