from ecdsa import SigningKey,SECP256k1
import select

sk = SigningKey.generate(SECP256k1) # uses NIST192p
print(sk)
vk = sk.get_verifying_key()
print(sk.to_der())
print(vk)
signature = sk.sign("message".encode(),hashfunc=sha256)
print(signature)
assert vk.verify(signature, "message".encode(),hashfunc=sha256)