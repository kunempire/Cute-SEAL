#include "test_BFV.hpp"

const int batch_size = 5;
const int test_times = 5; 
const String image_dir="../../../data/original";
const String encrypted_dir = "../../../data/encrypted";
const String log_file = "../../../log/BFV_int.log";

int main(int argc, char** argv) {

  // write log
  ofstream file(log_file);
  if (file.is_open()) {
    file << "batch_size per test: " << batch_size << "\n";
    file << "total test times: " << test_times << "\n\n";
    file.close();
  } else {
    cerr << "Error: Unable to open file." << endl;
    return 1;
  }

  /* generate context */
  EncryptionParameters parms(scheme_type::bfv);
  size_t poly_modulus_degree = 8192*4; // 注意大小要超过单个图像总像素匹配, 比如64*64灰度图像要小于8192
  parms.set_poly_modulus_degree(poly_modulus_degree);
  parms.set_coeff_modulus(CoeffModulus::BFVDefault(poly_modulus_degree));
  parms.set_plain_modulus(PlainModulus::Batching(poly_modulus_degree, 20));
  SEALContext context(parms);
  // show encryption parameters
  print_line(__LINE__);
  std::cout << "Set encryption parameters and print" << endl;
  print_parameters(context);

  /* initial tools */
  KeyGenerator keygen(context);
  auto secret_key = keygen.secret_key();
  PublicKey public_key;
  keygen.create_public_key(public_key);
  RelinKeys relin_keys;
  keygen.create_relin_keys(relin_keys);
  GaloisKeys gal_keys;
  keygen.create_galois_keys(gal_keys);
  Encryptor encryptor(context, public_key);
  Evaluator evaluator(context);
  Decryptor decryptor(context, secret_key);
  BatchEncoder batch_encoder(context);

  // read image path
  vector<string> image_list;
  for (const auto& entry : filesystem::directory_iterator(image_dir)) {
      if (entry.path().extension() == ".png") {
          image_list.push_back(entry.path().string());
      }
  }

  vector<double> average_encryption;
  vector<double> average_query;


	for(int i = 0; i < test_times ; ++i ){
    file.open(log_file, ios::app);
    if (file.is_open()) {
      file << "Testing: " << i + 1 << "/" << test_times << "\n";
      file.close();
    } else {
      cerr << "Error: Unable to open file." << endl;
      return 1;
    }
    // random sample
    random_device rd;
    mt19937 g(rd());
    vector<string> random_images;
    shuffle(image_list.begin(), image_list.end(),g);
    random_images.assign(image_list.begin(), image_list.begin() + batch_size);

    // read images
    vector<Mat> images;
    for (const auto& image_path : random_images) {
        Mat image = cv::imread(image_path, IMREAD_UNCHANGED);
        if (!image.data) {
            cerr << "Error: Could not read image " << image_path << endl;
            return 1;
        }
        resize(image, image, Size(64, 64));
        // Mat gray_image;
        // cvtColor(image,gray_image, cv::COLOR_BGR2GRAY);
        images.push_back(image);
    }

    // Encrypt
    auto start_time = chrono::high_resolution_clock::now();
    vector<Ciphertext> encrypted_images;
    for (const auto& image : images) {
      // flatten image
      vector<uint64_t> flattened_data;
      flattened_data.reserve(image.rows * image.cols * image.channels());
      for (int i = 0; i < image.rows; ++i) {
        for (int j = 0; j < image.cols; ++j) {
          flattened_data.push_back(static_cast<uint64_t>(image.at<uchar>(i, j)));
        }
      }

      Plaintext plaintext;
      batch_encoder.encode(flattened_data, plaintext);
      Ciphertext encrypted_data;
      encryptor.encrypt(plaintext, encrypted_data);
      encrypted_images.push_back(encrypted_data);
    }
  
    // Save encrypted_images to file
    for (size_t i = 0; i < encrypted_images.size(); ++i) {
        string filename = encrypted_dir + "/encrypted_image_" + to_string(i) + ".bin";
        ofstream file(filename, ios::binary);
        encrypted_images[i].save(file);
    }

    // Calculate encryption time
    auto end_time = chrono::high_resolution_clock::now();
    auto encryption_time = chrono::duration_cast<chrono::microseconds>(end_time - start_time).count();

    String query_image_path=random_images[1];

    start_time = chrono::high_resolution_clock::now();

    // read image
    Mat query_image = imread(query_image_path, IMREAD_UNCHANGED);
    if (!query_image.data) {
        cerr << "Error: Could not read image " << query_image_path << endl;
        return 1;
    }
    resize(query_image, query_image, Size(64, 64));

    // flatten
    vector<uint64_t> flattened_data;
    flattened_data.reserve(query_image.rows * query_image.cols * query_image.channels());
    for (int i = 0; i < query_image.rows; ++i) {
      for (int j = 0; j < query_image.cols; ++j) {
        flattened_data.push_back(static_cast<uint64_t>(query_image.at<uchar>(i, j)));
      }
    }
    Plaintext plaintext;
    batch_encoder.encode(flattened_data, plaintext);
    Ciphertext encrypted_query_image;
    encryptor.encrypt(plaintext, encrypted_query_image);

    vector<uint64_t> similarity_scores;

    for (size_t i = 0; i < encrypted_images.size(); ++i) {
      string filename = encrypted_dir + "/encrypted_image_" + to_string(i) + ".bin";
      ifstream file(filename, ios::binary);
      if (file.is_open()) {
        Ciphertext encrypted_text;
        encrypted_text.load(context, file);
        // similarity: cos<a, b> = a.dot(b) / |a||b|
        Ciphertext dot;
        evaluator.multiply(encrypted_query_image, encrypted_text, dot);
        Plaintext plain_dot;
        decryptor.decrypt(dot, plain_dot);

        vector<uint64_t> result_vector;
        batch_encoder.decode(plain_dot, result_vector);
        uint64_t sum = 0;
        for(int i = 0; i < result_vector.size(); ++i){
          sum += result_vector[i];
        }
        // similarity_score: cos<a, b>
        similarity_scores.push_back(sum);
    } else {
        cerr << "Error opening file: " << filename << endl;
    }  
   
}
    auto max_score_iter = max_element(similarity_scores.begin(), similarity_scores.end()); 
    size_t max_score_index = distance(similarity_scores.begin(), max_score_iter);
    // std::cout << "Index " << max_score_index << std::endl;  

    // Calculate query time
    end_time = chrono::high_resolution_clock::now();
    auto query_time = chrono::duration_cast<chrono::microseconds>(end_time - start_time).count();
    
    // write log
    double average_encryption_time = static_cast<double>(encryption_time) / static_cast<double>(batch_size);
    double average_query_time = static_cast<double>(query_time) / static_cast<double>(batch_size);
    file.open(log_file, ios::app);
    if (file.is_open()) {
      file << fixed << setprecision(4);
      file << "Test" << i << "/" << test_times << " Result: \n";
      file << "Average Encryption Time: " << average_encryption_time / 1e6 << " seconds / image\n";
      file << "Average Query Time: " << average_query_time / 1e6 << " seconds / image\n\n";
      file.close();
    } else {
      cerr << "Error: Unable to open file." << endl;
      return 1;
    }
    average_encryption.push_back(average_encryption_time);
    average_query.push_back(average_query_time);
  }

  double average_encryption_sum = 0.0;
  double average_query_sum = 0.0;
  for (int i = 0; i < average_encryption.size(); ++i){
    average_query_sum += average_query[i];
    average_encryption_sum += average_encryption[i];
  }


  // write log
  file.open(log_file, ios::app);
  if (file.is_open()) {
    file << fixed << setprecision(4);
    file << "Finally Result: \n";
    file << "Average Encryption Time: " << average_encryption_sum / test_times / 1e6<< " seconds / image\n";
    file << "Average Query Time: " << average_query_sum / test_times  / 1e6 << " seconds / image\n\n";
    file.close();
  } else {
    cerr << "Error: Unable to open file." << endl;
    return 1;
  }
  return 0;
}