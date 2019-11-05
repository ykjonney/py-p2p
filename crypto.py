import sha3
import ecdsa

def keccak256(s):
    k= sha3.keccak_256()
    k.update(s)
    return k.digest()

def generate_key():
    sk=ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    a=sk.to_pem()
    with open('private.txt','wb') as w:
        w.write(a)
    return a
def get_key(path):
    with open(path,'rb') as f:
       key=f.read()
    return key

if __name__=="__main__":
   a=get_key('private.txt')
   b=ecdsa.SigningKey.from_pem(a).sign('aa'.encode())
   vk=ecdsa.SigningKey.from_pem(a).get_verifying_key()
   c=keccak256(b)
   print(c)
   if vk.verify(b,'aa'.encode()):
       print('ok')

