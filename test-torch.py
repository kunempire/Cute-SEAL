import tenseal as ts
import os
import random
import time
from tqdm import tqdm
import torch
from torchvision.io import read_image
from torchvision import transforms

batch_size = 5
test_times = 5
image_dir = 'data/original'
encrypted_dir = 'data/encrypted'
log_file = 'log/test-torch.log'
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192*4, coeff_mod_bit_sizes=[60, 40, 40, 60])  # Algorithm: CKKS
context.global_scale = 2**40
context.generate_galois_keys()

with open(log_file, 'w') as file:
    content = 'batch_size per test: {}\ntotal test times: {}'.format(batch_size, test_times)
    file.write(content)

# Ensure that PyTorch is using GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Get image_path list
image_list = [os.path.join(image_dir, image) for image in os.listdir(image_dir) if image.endswith('.png')]

# recording test times
test_encrypt_times = []
test_query_times = []

for times in range(test_times):
    print("\033[94mTesting: {}/{}\033[0m".format(times+1, test_times))
    with open(log_file, 'a') as file:
        file.write("\n\n")
        content = "Testing: {}/{}\n".format(times+1, test_times)
        file.write(content)

    # Randomly select images
    random_images = random.sample(image_list, batch_size)

    start_time = time.perf_counter()
    # Image to PyTorch tensor
    images = [transforms.Resize((64, 64))(read_image(image).to(device)) for image in random_images]
    images = [transforms.ToTensor()(transforms.ToPILImage()(image)).float() for image in images]

    # Encrypt
    encrypted_images = []
    for image in tqdm(images, desc="Encrypting images", unit="image"):
        # 将 PyTorch GPU 张量直接传递给 ts.ckks_vector
        encrypted_vector = ts.ckks_vector(context, image.view(-1).tolist())
        encrypted_images.append(encrypted_vector)

    # Save encrypted_images to file
    pbar = tqdm(total=len(encrypted_images), desc="Saving encrypted images", unit="image")

    for i, encrypted_image in enumerate(encrypted_images):
        with open("{}/encrypted_image_{}.pkl".format(encrypted_dir, i), "wb") as f:
            f.write(encrypted_image.serialize())

        pbar.update(1)

    pbar.close()

    # Calculate encryption time
    encryption_time = (time.perf_counter() - start_time)  # to microseconds: * 1e6
    average_encryption_time = encryption_time / batch_size

    # Query to match
    query_image_path = random_images[3]

    start_time = time.perf_counter()

    # Encrypt query_image
    query_image = transforms.Resize((64, 64))(read_image(query_image_path).to(device))
    query_image = transforms.ToTensor()(transforms.ToPILImage()(query_image)).float()    
    encrypted_query_image = ts.ckks_vector(context, query_image.view(-1).tolist())

    similarity_scores = []

    pbar = tqdm(total=len(encrypted_images), desc="Querying images", unit="image")
    for i in range(len(encrypted_images)):
        with open("{}/encrypted_image_{}.pkl".format(encrypted_dir, i), "rb") as f:
            encrypted_image = ts.ckks_vector_from(context, f.read())
            dot_image = encrypted_query_image.dot(encrypted_image)
            similarity_score = dot_image.decrypt()[0]
            similarity_scores.append(similarity_score)
        pbar.update(1)
    pbar.close()

    query_time = (time.perf_counter() - start_time)  # * 1e6
    average_query_time = query_time / batch_size

    print("\033[92mTest{}/{} Result: ".format(times+1, test_times))
    print("Average Encryption Time: {:.4f} seconds / image".format(average_encryption_time))
    print("Average Query Time: {:.4f} seconds / image\033[0m".format(average_query_time))
    with open(log_file, 'a') as file:
        file.write("Test{}/{} Result: ".format(times+1, test_times))
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
