from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import numpy as np

def encrypt(image, key):
    # Convert the image to a NumPy array
    img_array = np.array(image)

    # Flatten the array and convert it to bytes
    pixel_data = img_array.flatten().tobytes()

    # Generate a random 128-bit IV for the block cipher mode
    iv = get_random_bytes(16)
 
    block_size = 16  # 16 bytes = 128 bits
    plaintext_blocks = [pixel_data[i:i+block_size] for i in range(0, len(pixel_data), block_size)]

    # Use IV and key to encrypt first plaintext block using AES-128 in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_blocks = [cipher.encrypt(plaintext_blocks[0])]

    # Use encrypted ciphertext and key to encrypt subsequent plaintext blocks using ChaCha20 stream cipher
    for i in range(1, len(plaintext_blocks)):
        cipher = ChaCha20.new(key=key, nonce=encrypted_blocks[-1][:12])
        encrypted_blocks.append(cipher.encrypt(plaintext_blocks[i]))
 
    # Combine encrypted IV and data
    encrypted_image_data = iv + b''.join(encrypted_blocks)  

    # Create a new PIL image from the encrypted data
    encrypted_image = Image.frombytes('RGB', image.size, encrypted_image_data)
    # Save the encrypted image in the same format as the original image
    encrypted_image_path = "encrypted_image.jpeg"
    encrypted_image.save(encrypted_image_path, format=image.format)
    print("Encrypted image saved as:", encrypted_image_path)

    return  encrypted_image_data

def decrypt( encrypted_image_data, key,width, height): 
      # Divide encrypted pixels into blocks of 128 bits
    block_size = 16  # 16 bytes = 128 bits
    encrypted_blocks = [ encrypted_image_data[i:i+block_size] for i in range(0, len( encrypted_image_data), block_size)]

    # Split the first 16 bytes as IV for AES decryption
    iv = encrypted_blocks.pop(0)

    # Use IV and key to decrypt first pixel block using AES-128 in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_blocks = [cipher.decrypt(encrypted_blocks[0])]

    # Use decrypted pixels and key to decrypt subsequent blocks using ChaCha20 stream cipher
    for i in range(1, len(encrypted_blocks)):
        cipher = ChaCha20.new(key=key, nonce=encrypted_blocks[i-1][:12])
        decrypted_blocks.append(cipher.decrypt(encrypted_blocks[i]))

    # Combine decrypted pixel blocks
    decrypted_pixels = b''.join(decrypted_blocks)
     # Create a new PIL image from the decrypted pixels
    image = Image.frombytes('RGB', (width, height), decrypted_pixels)

    return image


print("*****Image Encryption Using Hybrid AES-128 and ChaCha20 Cipher*****")
key = get_random_bytes(32)  # 256-bit key

# Open the original image
original_image_path = "test1.jpeg"
image = Image.open(original_image_path)
# Get the width and height of the image
width, height = image.size 

print("Encrypting Image...")
# Encrypt the image
encrypted_image = encrypt(image, key)

print("Decrypting Image...")
# Decrypt the encrypted image
decrypted_image = decrypt(encrypted_image, key,width, height)
 
# Save the decrypted image in the same format as the original image
decrypted_image_path = "decrypted_image.jpeg"
decrypted_image.save(decrypted_image_path, format=image.format)
print("Decrypted image saved as:", decrypted_image_path)
