#define _CRT_SECURE_NO_WARNINGS

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <omp.h>

typedef struct {
	int *A, *B, *C;
	int n, m;
} DataSet;

void fillDataSet(DataSet *dataSet);
void printDataSet(DataSet dataSet);
void closeDataSet(DataSet dataSet);
void add(DataSet dataSet);

int main(int argc, char *argv[]) {
	#ifndef _OPENMP
	printf("OpenMP is not supported, sorry!\n");
	getchar();
	return 0;
	#endif

	#define NUMOFTHREAD 4

	DataSet dataSet;
	if (argc < 3) {
		printf("[-] Invalid No. of arguments.\n");
		printf("[-] Try -> <n> <m> \n");
		printf(">>> ");
		scanf("%d %d", &dataSet.n, &dataSet.m);
	}
	else {
		dataSet.n = atoi(argv[1]);
		dataSet.m = atoi(argv[2]);
	}

	omp_set_num_threads(NUMOFTHREAD);

	fillDataSet(&dataSet);
	add(dataSet);
	//printDataSet(dataSet);
	closeDataSet(dataSet);
	system("PAUSE");

	return EXIT_SUCCESS;
}

void fillDataSet(DataSet *dataSet) {
	int i, j;

	dataSet->A = (int *)malloc(sizeof(int) * dataSet->n * dataSet->m);
	dataSet->B = (int *)malloc(sizeof(int) * dataSet->n * dataSet->m);
	dataSet->C = (int *)malloc(sizeof(int) * dataSet->n * dataSet->m);

	srand(time(NULL));
	#pragma omp parallel for 
	for (i = 0; i < dataSet->n; i++) {
		for (j = 0; j < dataSet->m; j++) {
			dataSet->A[i*dataSet->m + j] = rand() % 100;
			dataSet->B[i*dataSet->m + j] = rand() % 100;
		}
	}
}

void printDataSet(DataSet dataSet) {
	int i, j;

	printf("[-] Matrix A\n");
	for (i = 0; i < dataSet.n; i++) {
		for (j = 0; j < dataSet.m; j++) {
			printf("%-4d", dataSet.A[i*dataSet.m + j]);
		}
		putchar('\n');
	}

	printf("[-] Matrix B\n");
	for (i = 0; i < dataSet.n; i++) {
		for (j = 0; j < dataSet.m; j++) {
			printf("%-4d", dataSet.B[i*dataSet.m + j]);
		}
		putchar('\n');
	}

	printf("[-] Matrix C\n");
	for (i = 0; i < dataSet.n; i++) {
		for (j = 0; j < dataSet.m; j++) {
			printf("%-8d", dataSet.C[i*dataSet.m + j]);
		}
		putchar('\n');
	}
}

void closeDataSet(DataSet dataSet) {
	free(dataSet.A);
	free(dataSet.B);
	free(dataSet.C);
}

void add(DataSet dataSet) {
	double starttime, elapsedtime, average_elapsedtime = 0;
	int epoch = 10;
	int i, j;

	// One-Diementional Data Row Decomposition parallelism
	// 512 * 512, 16384 * 16384
	for (int k = 0; k < epoch; k++) {
		starttime = omp_get_wtime();

		/*#pragma omp parallel for private (j) schedule (static, 1)
		for (i = 0; i < dataSet.n; i++) {
			for (j = 0; j < dataSet.m; j++) {
				dataSet.C[i * dataSet.m + j] = dataSet.A[i * dataSet.m + j] + dataSet.B[i * dataSet.m + j];
			}
		}*/

		// One-Diementional Data Column Decomposition parallelism
		// 512 * 512, 16384 * 16384
		/*#pragma omp parallel for private (i) schedule (static, 1)
		for (j = 0; j < dataSet.n; j++) {
			for (i = 0; i < dataSet.m; i++) {
				dataSet.C[i * dataSet.m + j] = dataSet.A[i * dataSet.m + j] + dataSet.B[i * dataSet.m + j];
			}
		}*/

		// Two-Diementional Data Decomposition parallelism
		// 512 * 512, 16384 * 16384
		/*omp_set_max_active_levels(2);
		#pragma omp parallel for schedule (static, 128)
		for (int i = 0; i < dataSet.n; i++) {
			#pragma omp parallel for schedule (static, 128)
			for (int j = 0; j < dataSet.m; j++) {
				dataSet.C[i * dataSet.m + j] = dataSet.A[i * dataSet.m + j] + dataSet.B[i * dataSet.m + j];
			}
		}*/

		// Collapse For parallelism
		// 512 * 512, 16384 * 16384
		/*omp_set_max_active_levels(2);
		#pragma omp parallel for collapse(2) schedule(static, 128)
		for (int i = 0; i < dataSet.n; i++) {
			for (int j = 0; j < dataSet.m; j++) {
				dataSet.C[i * dataSet.m + j] =
					dataSet.A[i * dataSet.m + j] + dataSet.B[i * dataSet.m + j];
			}
		}*/
#pragma omp parallel for schedule(static, 128)
		for (int ij = 0; ij < dataSet.n * dataSet.m; ij++) {
			dataSet.C[ij] = dataSet.A[ij] + dataSet.B[ij];
		}
		

		// get ending time and use it to determine elapsed time
		elapsedtime = omp_get_wtime() - starttime;
		// report elapsed time
		printf("Time Elapsed: %f Secs \n",
			elapsedtime);
		average_elapsedtime += elapsedtime;
	}
	printf("Average Time Elapsed: %f Secs \n",
		(average_elapsedtime / epoch));
}
