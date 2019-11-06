import sha3
import ecdsa, binascii


def keccak256(s):
    k = sha3.keccak_256()
    k.update(s)
    return k.digest()


def generate_key():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    a = sk.to_pem()
    with open('private.txt', 'wb') as w:
        w.write(a)
    return a


def get_key(path):
    with open(path, 'rb') as f:
        key = f.read()
    return key


def int_to_big_endian(large_num):
    if large_num == 0:
        return b'\x00'
    s = hex(large_num)
    s = s[2:]
    s = s.rstrip('L')
    if len(s) & 1:
        s = '0' + s
    s = binascii.a2b_hex(s)
    return s


if __name__ == "__main__":
    a = get_key('private.txt')
    b = ecdsa.SigningKey.from_pem(a).sign('aa'.encode())
    vk = ecdsa.SigningKey.from_pem(a).get_verifying_key()
    c = keccak256(b)
    print(len(c))
    diff = ord('a') ^ ord('b')
    print(diff)
    print(len('{:b}'.format(diff)))
    if vk.verify(b, 'aa'.encode()):
        print('ok')
