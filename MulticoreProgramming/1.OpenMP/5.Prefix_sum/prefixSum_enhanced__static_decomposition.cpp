#define _CRT_SECURE_NO_WARNINGS

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <omp.h>

void omp_check();
void fill_array(int *a, size_t n);
void prefix_sum(int *a, size_t n);
void print_array(int *a, size_t n);

#define NUMOFTHREAD 4

int main(int argc, char *argv[]) {
	// Check for correct compilation settings
	omp_set_max_active_levels(2);

	omp_check();
	// Input N
	size_t n = 0;
	printf("[-] Please enter N: ");
	scanf("%uld\n", &n);
	// Allocate memory for array
	int * a = (int *)malloc(n * sizeof a);
	// Fill array with numbers 1..n
	fill_array(a, n);
	// Print array
	//print_array(a, n);
	// Compute prefix sum
	prefix_sum(a, n);
	//Print array
	//print_array(a, n);
	// Free allocated memory
	free(a);
	return EXIT_SUCCESS;
}

void prefix_sum(int *a, size_t n) {
	double starttime, elapsedtime;
	int i;
	int prefix_sum_parts[NUMOFTHREAD];
	int part_size = n / NUMOFTHREAD;
	starttime = omp_get_wtime();
	omp_set_num_threads(NUMOFTHREAD);
#pragma omp parallel
	{
		int id_threads = omp_get_thread_num();
		int n_threads = omp_get_num_threads();

		for (i = 1; i < part_size; ++i) {
			a[id_threads * part_size + i] = a[id_threads * part_size + i] + a[id_threads * part_size + i - 1];
		}

		prefix_sum_parts[id_threads] = a[(id_threads + 1) * part_size - 1];


#pragma omp barrier
#pragma omp single
		for (int i = 1; i < NUMOFTHREAD; ++i) {
			prefix_sum_parts[i] +=  prefix_sum_parts[i - 1];
		}

#pragma omp barrier
		for (int j = 0; j < part_size; j++) {
			if (id_threads == 0) {
				continue;
			}
			a[id_threads * part_size + j] += prefix_sum_parts[id_threads-1];
		}
	}
	// get ending time and use it to determine elapsed time
	elapsedtime = omp_get_wtime() - starttime;
	// report elapsed time
	printf("Time Elapsed: %f Secs \n",
		elapsedtime);
}

void print_array(int *a, size_t n) {
	int i;
	printf("[-] array: ");
	for (i = 0; i < n; ++i) {
		printf("%d, ", a[i]);
	}
	printf("\b\b  \n");
}

void fill_array(int *a, size_t n) {
	int i;
#pragma omp for
	for (i = 0; i < n; ++i) {
		a[i] = i + 1;
	}
}

void omp_check() {
	printf("------------ Info -------------\n");
#ifdef _DEBUG
	printf("[!] Configuration: Debug.\n");
#pragma message ("Change configuration to Release for a fast execution.")
#else
	printf("[-] Configuration: Release.\n");
#endif // _DEBUG
#ifdef _M_X64
	printf("[-] Platform: x64\n");
#elif _M_IX86 
	printf("[-] Platform: x86\n");
#pragma message ("Change platform to x64 for more memory.")
#endif // _M_IX86 
#ifdef _OPENMP
	printf("[-] OpenMP is on.\n");
	printf("[-] OpenMP version: %d\n", _OPENMP);
#else
	printf("[!] OpenMP is off.\n");
	printf("[#] Enable OpenMP.\n");
#endif // _OPENMP
	printf("[-] Maximum threads: %d\n", omp_get_max_threads());
	printf("[-] Nested Parallelism: %s\n", omp_get_nested() ? "On" : "Off");
#pragma message("Enable nested parallelism if you wish to have parallel region within parallel region.")
	printf("===============================\n");
}
