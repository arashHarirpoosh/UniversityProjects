#include <stdlib.h>
#include <stdio.h>
#include <omp.h>


void constantInit(float *data, int size, float val);
void mulMat(float * a, float *b, float *c, int n);
void printMat(float * v, int n);

int main()
{
	const int n = 512;
	const float valB = 0.01f;
	unsigned int arr_size = n * n;
	float * a;
	float * b;
	float * c;
	double elapsedtime, starttime;
	a = (float*)malloc(sizeof(float)*arr_size);
	b = (float*)malloc(sizeof(float)*arr_size);
	c = (float*)malloc(sizeof(float)*arr_size);

	constantInit(a, arr_size, 1.0f);
	constantInit(b, arr_size, valB);

	starttime = omp_get_wtime();

	mulMat(a, b, c, n);

	elapsedtime = omp_get_wtime() - starttime;


	/*printMat(a, n);
	printMat(b, n);
	printMat(c, n);*/

	// report elapsed time
	printf("Time Elapsed %f ms\n", elapsedtime * 1000);

	return EXIT_SUCCESS;
}

// Fills a Matrice with data
void constantInit(float *data, int size, float val)
{
	for (int i = 0; i < size; ++i)
	{
		data[i] = val;
	}
}

// Multiplys two Matrices
void mulMat(float * a, float *b, float *c, int n) {
	for (int row = 0; row < n; row++) {
		for (int col = 0; col < n; col++) {
			float C_val = 0;
			for (int k = 0; k < n; ++k) {
				float A_elem = a[row * n + k];
				float B_elem = b[k * n + col];
				C_val += A_elem * B_elem;
			} 
			c[row*n + col] = C_val;
		}
	}

}

// Prints a Matrices to the stdout.
void printMat(float * v, int n) {
	printf("[-] Vector elements: \n");
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++)
			printf("%f	", v[i*n + j]);
		printf("\n");
	}
	printf("\b\b \n");
}