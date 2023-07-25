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

    # # Create AES cipher object with CBC mode and the generated IV
    # cipher_aes = AES.new(key, AES.MODE_CBC, iv)

    # # Pad the pixel data to the block size of AES
    # padded_data = pad(pixel_data, AES.block_size)

    # # Encrypt the padded data
    # encrypted_data = cipher_aes.encrypt(padded_data)

    # # Use encrypted data and key to encrypt the IV using ChaCha20 stream cipher
    # cipher_chacha = ChaCha20.new(key=key[:32])
    # encrypted_iv = cipher_chacha.encrypt(iv)

    # Divide plaintext into blocks of 128 bits
    block_size = 16  # 16 bytes = 128 bits
    plaintext_blocks = [pixel_data[i:i+block_size] for i in range(0, len(pixel_data), block_size)]

    # Use IV and key to encrypt first plaintext block using AES-128 in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_blocks = [cipher.encrypt(plaintext_blocks[0])]

    # Use encrypted ciphertext and key to encrypt subsequent plaintext blocks using ChaCha20 stream cipher
    for i in range(1, len(plaintext_blocks)):
        cipher = ChaCha20.new(key=key, nonce=encrypted_blocks[-1][:12])
        encrypted_blocks.append(cipher.encrypt(plaintext_blocks[i]))

    # Combine encrypted ciphertext and IV

    # Combine encrypted IV and data
    encrypted_image_data = iv + b''.join(encrypted_blocks) 
    # print(encrypted_blocks)

    # Create a new PIL image from the encrypted data
    encrypted_image = Image.frombytes('RGB', image.size, encrypted_image_data)
    # Save the encrypted image in the same format as the original image
    encrypted_image_path = "encrypted_image.jpeg"
    encrypted_image.save(encrypted_image_path, format=image.format)
    print("Encrypted image saved as:", encrypted_image_path)

    return  encrypted_image

def decrypt( encrypted_image, key,width, height):
    # Convert the encrypted image to a NumPy array
    encrypted_array = np.array(encrypted_image)

    # Flatten the array and convert it to bytes
    encrypted_image_data = encrypted_array.flatten().tobytes()

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
    # # Split the encrypted data into IV and encrypted pixels
    # encrypted_iv = encrypted_data[:16]
    # encrypted_pixels = encrypted_data[16:]
    #  # Divide encrypted pixels into blocks of 128 bits
    # block_size = 16  # 16 bytes = 128 bits
    # encrypted_blocks = [encrypted_pixels[i:i+block_size] for i in range(0, len(encrypted_pixels), block_size)]

    # # Use key and encrypted IV to decrypt the IV using ChaCha20 stream cipher
    # cipher_chacha = ChaCha20.new(key=key[:32])
    # iv = cipher_chacha.decrypt(encrypted_iv)

    # # Create AES cipher object with CBC mode and the decrypted IV
    # cipher_aes = AES.new(key, AES.MODE_CBC, iv)

    # # Decrypt the encrypted pixels
    # decrypted_pixels = cipher_aes.decrypt(encrypted_blocks)

    # # Remove the padding from the decrypted pixels
    # unpadded_data = unpad(decrypted_pixels, AES.block_size)

    # Create a new PIL image from the decrypted data
    # decrypted_image = Image.frombytes('RGB', encrypted_image.size, decrypted_pixels)

    # return decrypted_image

key = get_random_bytes(32)  # 256-bit key for AES-256 and ChaCha20

# Open the original image
original_image_path = "sample.jpeg"
image = Image.open(original_image_path)
# Get the width and height of the image
width, height = image.size
print("Original Image:")
# image.show()

# Encrypt the image
encrypted_image = encrypt(image, key)

# Display the encrypted image as pixels
print("Encrypted Image (Pixels):")
# encrypted_image.show()

# # Save the encrypted image in the same format as the original image
# encrypted_image_path = "encrypted_image.jpeg"
# encrypted_image.save(encrypted_image_path, format=image.format)
# print("Encrypted image saved as:", encrypted_image_path)

# Decrypt the encrypted image
decrypted_image = decrypt(encrypted_image, key,width, height)

# Display the decrypted image
print("Decrypted Image:")
# decrypted_image.show()

# Save the decrypted image in the same format as the original image
decrypted_image_path = "decrypted_image.jpeg"
decrypted_image.save(decrypted_image_path, format=image.format)
print("Decrypted image saved as:", decrypted_image_path)
