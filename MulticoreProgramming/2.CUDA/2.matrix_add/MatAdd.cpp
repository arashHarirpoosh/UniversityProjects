#include <stdlib.h>
#include <stdio.h>
#include <omp.h>


void fillMat(int * v, int matSizeX,int matSizeY);
void addMat(int * a, int *b, int *c, int matSizeX, int matSizeY);
void printMat(int * v, int matSizeX,int matSizeY);

int main()
{
	const int matSizeX = 32;
	const int matSizeY = 32;
	int * a;
	int * b;
	int * c;
	double elapsedtime, starttime;
	a = (int*)malloc(sizeof(int)*matSizeX*matSizeY);
	b = (int*)malloc(sizeof(int)*matSizeX*matSizeY);
	c = (int*)malloc(sizeof(int)*matSizeX*matSizeY);

	fillMat(a, matSizeX, matSizeY);
	fillMat(b, matSizeX, matSizeY);

	starttime = omp_get_wtime();

	addMat(a, b, c, matSizeX, matSizeY);

	elapsedtime = omp_get_wtime() - starttime;


	printMat(a, matSizeX, matSizeY);
	printMat(b, matSizeX, matSizeY);
	printMat(c, matSizeX, matSizeY);

	// report elapsed time
	printf("Time Elapsed %f ms\n", elapsedtime*1000);

	return EXIT_SUCCESS;
}

// Fills a Matrice with data
void fillMat(int * v, int matSizeX,int matSizeY) {
	static int L=0;
	for (int i = 0; i < matSizeX; i++) {
		for(int j =0 ; j<matSizeY;j++)
		v[i*matSizeY+j] = L++;
		

	}
}

// Adds two Matrices
void addMat(int * a, int *b, int *c, int matSizeX, int matSizeY) {
	int i;
	for (int i = 0; i < matSizeX; i++) {
		for (int j = 0; j < matSizeY; j++)
			c[i*matSizeY + j] = a[i*matSizeY + j]+ b[i*matSizeY + j];

	}
}

// Prints a Matrices to the stdout.
void printMat(int * v, int matSizeX ,int matSizeY) {
	int i;
	printf("[-] Vector elements: \n");
	for (int i = 0; i < matSizeX; i++) {
		for (int j = 0; j < matSizeY; j++)
			printf("%d	", v[i*matSizeY + j]);
		printf("\n");

	}
	printf("\b\b  \n");
}
