import sys

path = r'c:\Users\gromd\OneDrive\Документи\GitHub\Calogram\home.html'
with open(path, 'rb') as f:
    raw = f.read()

# Strip BOM
if raw[:3] == b'\xef\xbb\xbf':
    raw = raw[3:]

# The file was: original UTF-8 read as cp1251, then saved as UTF-8
# So current file = utf8_encode(cp1251_decode(original_utf8_bytes))
# Fix: utf8_decode(cp1251_encode(current_utf8_string))
garbled = raw.decode('utf-8')

# Encode back to cp1251 bytes (unencodable chars kept as-is)
result_bytes = bytearray()
i = 0
while i < len(garbled):
    c = garbled[i]
    try:
        b = c.encode('cp1251')
        result_bytes.extend(b)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # char not in cp1251 - was already a correct unicode char, keep as UTF-8
        result_bytes.extend(c.encode('utf-8'))
    i += 1

# Now decode as UTF-8
fixed = result_bytes.decode('utf-8')

# Verify
test_words = ['Вітаємо', 'Спожито', 'Ціль', 'Залишок', 'Поживні', 'Сніданок', 'Обід']
found = [w for w in test_words if w in fixed]
print('Found:', found)
print('Missing:', [w for w in test_words if w not in fixed])

if len(found) >= 5:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('SAVED OK, length:', len(fixed))
else:
    print('FIX FAILED - not saving')
    # Show sample
    idx = fixed.find('Р')
    if idx > 0:
        print('Still garbled?', repr(fixed[idx:idx+50]))
