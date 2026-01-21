import hashlib
k = "1690655150-the-big-bang-theory-2007"
h = hashlib.sha256(k.upper().encode()).hexdigest()
print(h)