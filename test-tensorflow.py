import tensorflow as tf
import tenseal as ts
import os
import random
import time
from tqdm import tqdm

batch_size = 5
test_times = 5 
image_dir = 'data/original'
encrypted_dir = 'data/encrypted'
log_file = 'log/test-tensorflow-CKKS.log'
# 变方案记得改下面的bfv/ckks_vector
# CKKS
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192*4, coeff_mod_bit_sizes=[60, 40, 40, 60])
context.global_scale = 2**40
# BFV
# context = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=8192*4, plain_modulus=786433)

context.generate_galois_keys()

# log file
with open(log_file, 'w') as file:
    content = 'batch_size per test: {}\ntotal test times: {}'.format(batch_size,test_times)
    file.write(content)

# Ensure that TensorFlow is using GPU
physical_devices = tf.config.list_physical_devices()
print(physical_devices)
print("Num GPUs Available: ", len(physical_devices)-1)
if len(physical_devices) > 1:
    tf.config.experimental.set_memory_growth(physical_devices[1], True)

# Get image_path list
image_list = [os.path.join(image_dir, image) for image in os.listdir(image_dir) if image.endswith('.png')]

# recording test times
test_encrypt_times =[]
test_query_times = []

for times in range(test_times):
    print("\033[94mTesting: {}/{}\033[0m".format(times+1,test_times))
    with open(log_file, 'a') as file:
        file.write("\n\n")
        content = "Testing: {}/{}\n".format(times+1,test_times)
        file.write(content)

    # Random to select images
    random_images = random.sample(image_list, batch_size)

    start_time = time.perf_counter()
    # Image to tf tensor
    images = [tf.io.read_file(image) for image in random_images]
    images = [tf.image.decode_png(image, channels=3) for image in images] # decode_jpeg/png/...
    images = [tf.image.resize(image, [64, 64]) for image in images]
    # images = [tf.image.convert_image_dtype(image, tf.float32) for image in images] # normalize to [0, 1]

    # Encrypt
    encrypted_images = []
    for image in tqdm(images, desc="Encrypting images", unit="image"):
        encrypted_vector = ts.ckks_vector(context, image.numpy().flatten().tolist())
        encrypted_images.append(encrypted_vector)

    # Save encrypted_images to file
    pbar = tqdm(total=len(encrypted_images), desc="Saving encrypted images", unit="image")

    for i, encrypted_image in enumerate(encrypted_images):
        with open("{}/encrypted_image_{}.pkl".format(encrypted_dir,i), "wb") as f:
            f.write(encrypted_image.serialize())

        pbar.update(1)

    pbar.close()

    # Calculate encryption time
    encryption_time = (time.perf_counter() - start_time) # to microseconds: * 1e6
    average_encryption_time = encryption_time / batch_size

    # Query to match
    query_image_path=random_images[3]

    start_time = time.perf_counter()

    # Encrypt query_image
    query_image = tf.io.read_file(query_image_path) 
    query_image = tf.image.decode_jpeg(query_image, channels=3)
    query_image = tf.image.resize(query_image, [64, 64])
    # query_image = tf.image.convert_image_dtype(query_image, tf.float32)
    encrypted_query_image = ts.ckks_vector(context, query_image.numpy().flatten().tolist())

    similarity_scores = []

    pbar = tqdm(total=len(encrypted_images), desc="Querying images", unit="image")
    for i in range(len(encrypted_images)):
        with open("{}/encrypted_image_{}.pkl".format(encrypted_dir,i), "rb") as f:
            encrypted_image = ts.ckks_vector_from(context, f.read())
            dot_image = encrypted_query_image.dot(encrypted_image)
            similarity_score = dot_image.decrypt()[0]
            similarity_scores.append(similarity_score)
            pbar.update(1)
    pbar.close()

    query_time = (time.perf_counter() - start_time) # * 1e6
    average_query_time = query_time / batch_size

    print("\033[92mTest{}/{} Result: \n".format(times+1,test_times))
    print("Average Encryption Time: {:.4f} seconds / image".format(average_encryption_time))
    print("Average Query Time: {:.4f} seconds / image\033[0m".format(average_query_time))
    with open(log_file, 'a') as file:
        file.write("Test{}/{} Result: ".format(times+1,test_times))
        file.write("Average Encryption Time: {:.4f} seconds / image\n".format(average_encryption_time))
        file.write("Average Query Time: {:.4f} seconds / image".format(average_query_time))

    test_encrypt_times.append(average_encryption_time)
    test_query_times.append(average_query_time)
    

average_encryption_time = sum(test_encrypt_times) / len(test_encrypt_times)
average_query_time = sum(test_query_times) / len(test_query_times)
print("\033[91mFinally Result: ")
print("Average Encryption Time: {:.4f} seconds / image".format(average_encryption_time))
print("Average Query Time: {:.4f} seconds / image\033[0m".format(average_query_time))
with open(log_file, 'a') as file:
    file.write("\n\n")
    file.write("Finally Result: ")
    file.write("Average Encryption Time: {:.4f} seconds / image\n".format(average_encryption_time))
    file.write("Average Query Time: {:.4f} seconds / image".format(average_query_time))
    