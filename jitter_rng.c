#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>
#include <openssl/evp.h>
#include <string.h>

// ===== XORSHIFT =====
uint64_t s[2] = { 0x123456789ABCDEF0, 0x0FEDCBA987654321 };

uint64_t xorshift128plus(void) {
    uint64_t s1 = s[0];
    const uint64_t s0 = s[1];
    s[0] = s0;
    s1 ^= s1 << 23; 
    s[1] = s1 ^ s0 ^ (s1 >> 18) ^ (s0 >> 5);
    return s[1] + s0;
}

// ===== WORKLOAD =====
void dummy_work() {
    volatile int arr[5] = {5, 2, 4, 1, 3};
    for(int i = 0; i < 4; i++) {
        for(int j = 0; j < 4-i; j++) {
            if(arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}

int main() {
    FILE *f = fopen("data.bin", "wb");
    if (!f) return 1;

    int bytes_to_generate = 1000000;

    // ===== AES-256 CTR SETUP =====
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();

    uint8_t key[32];  // 256-bit key
    uint8_t iv[16];   // counter (IV)

    // Seed klucza i IV z XORSHIFT (czyli z jittera pośrednio)
    for(int i = 0; i < 32; i++) key[i] = xorshift128plus() & 0xFF;
    for(int i = 0; i < 16; i++) iv[i] = xorshift128plus() & 0xFF;

    EVP_EncryptInit_ex(ctx, EVP_aes_256_ctr(), NULL, key, iv);

    for(int i = 0; i < bytes_to_generate; i++) {

        uint8_t raw_byte = 0;

        // ===== GENERACJA SUROWEGO BAJTU =====
        for(int b = 0; b < 8; b++) {
            uint64_t start = __rdtsc();
            dummy_work(); 
            uint64_t end = __rdtsc();

            uint64_t delta = end - start;
            uint8_t hardware_bit = delta & 1;

            s[0] ^= hardware_bit;
            uint64_t prng_val = xorshift128plus();

            raw_byte = (raw_byte << 1) | (prng_val & 1);
        }

        // ===== AES-CTR POST-PROCESSING =====
        uint8_t out_byte;
        int out_len;

        EVP_EncryptUpdate(ctx, &out_byte, &out_len, &raw_byte, 1);

        fwrite(&out_byte, 1, 1, f);
    }

    EVP_CIPHER_CTX_free(ctx);
    fclose(f);
    return 0;
}
