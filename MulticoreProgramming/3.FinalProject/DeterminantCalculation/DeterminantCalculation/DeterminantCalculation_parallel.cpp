// C++ program to find Deteminant of a matrix  
#include <math.h> 
#include<omp.h>
#include "fstream"      
#include "string" 
#include <filesystem>
#include <iostream>
using namespace std;

// Dimension of input square matrix   
#define N 512
#define epoch 10

void LoadMatrix(long double ** matrix, string path);
void  GaussianElimination(long double **A, long double **L, long double **U, int s, int n) {
	int r = s + n;
#pragma omp parallel for
	for (int i = s; i < r; i++)
	{
		for (int j = s; j < r; j++)
		{
			U[i][j] = A[i][j];

		}
	}

	for (int i = s + 1; i < r; i++)
	{
#pragma omp parallel for
		for (int j = i; j < r; j++)
		{
			long double coefficient = U[j][i - 1] / U[i - 1][i - 1];
			for (int k = s; k < r; k++)
			{
				U[j][k] -= coefficient * U[i - 1][k];
			}
			L[j][i - 1] += coefficient * L[i - 1][i - 1];
		}
	}

}

void BlockLUDecomposition(long double **A, long double **L, long double **U, int s, int n) {
	if (n - s < 16) {
		GaussianElimination(A, L, U, s, n - s);
	}
	else
	{
		int b = min(64, max(16, int(n / 8)));
		int r = n - b, c = s + b;

		// Calculate U00
		GaussianElimination(A, L, U, s, b);

#pragma omp parallel sections num_threads( 4 )
		{
			// Calculate L10
#pragma omp section
			{
#pragma omp parallel for num_threads( 2 )
				for (int k = s; k < r; k++)
				{
					for (int i = s; i < c; i++)
					{
						long double sum = 0;
						for (int j = s; j < i; j++)
						{
							sum += L[b + k][j] * U[j][i];
						}
						L[b + k][i] = (A[b + k][i] - sum) / U[i][i];
					}

				}
			}
			// Calculate U01
#pragma omp section 
			{
#pragma omp parallel for num_threads( 2 )
				for (int k = s; k < c; k++)
				{
					for (int i = s; i < r; i++)
					{
						long double sum = 0;
						for (int j = s; j < k; j++)
						{
							sum += L[k][j] * U[j][b + i];
						}

						U[k][b + i] = (A[k][b + i] - sum);
					}

				}
			}
		}
		// Calculate (A11)'
		// Multiply L10, U01
		for (int k = s; k < r; k++)
		{
#pragma omp parallel for
			for (int i = s; i < r; i++)
			{
				long double sum = 0;
				for (int j = s; j < s + b; j++)
				{
					sum += L[b + k][j] * U[j][b + i];
				}

				A[b + k][b + i] -= sum;
			}
		}

		BlockLUDecomposition(A, L, U, c, n);
	}

}

long double determinant(long double **mat)
{

	long double det = mat[0][0];
#pragma omp parallel for reduction(*:det)
	for (int i = 1; i < N; i++)
	{
		det *= mat[i][i];
	}
	return det;
}


void LoadMatrix(long double ** matrix, string path) {
	int x, y;
	ifstream mat(path);

	if (!mat) {
		cout << "Cannot open file.\n";
		return;
	}

	for (y = 0; y < N; y++) {
		for (x = 0; x < N; x++) {
			mat >> matrix[x][y];
		}
	}

	mat.close();
}


// Driver code  
int main()
{
	double average_all_elapsedtime = 0;
	int num_of_files = 0;
	// open a file in write mode.
	ofstream outfile;
	outfile.open("data_out\\512_results.txt");
	omp_set_num_threads(4);

	namespace fs = std::experimental::filesystem;//std::filesystem
	std::string path = "data_in\\512";
	for (const auto & entry : fs::directory_iterator(path))
	{
		num_of_files++;
		long double **matrix = (long double **)malloc(N * sizeof(long double *));
		long double **copy_matrix = (long double **)malloc(N * sizeof(long double *));
		long double **L = (long double **)malloc(N * sizeof(long double *));
		long double **U = (long double **)malloc(N * sizeof(long double *));

		for (int i = 0; i < N; i++) {
			matrix[i] = (long double *)malloc(N * sizeof(long double));
			copy_matrix[i] = (long double *)malloc(N * sizeof(long double));
			L[i] = (long double *)malloc(N * sizeof(long double));
			U[i] = (long double *)malloc(N * sizeof(long double));
		}

#pragma omp parallel
		{
#pragma omp single nowait
			LoadMatrix(matrix, entry.path().string());
#pragma omp for nowait
			for (int i = 0; i < N; i++) {
				L[i][i] = 1;
			}
		}
#pragma omp parallel for
		for (int i = 0; i < N; i++)
		{
			for (int j = 0; j < N; j++)
			{
				copy_matrix[i][j] = matrix[i][j];
			}

		}
		double starttime, elapsedtime, average_elapsedtime = 0;
		long double det_u;
		for (int i = 0; i < epoch; i++)
		{
			starttime = omp_get_wtime();
			BlockLUDecomposition(matrix, L, U, 0, N);
			// Calculate Determinant
			det_u = determinant(U);

			// get ending time and use it to determine elapsed time
			elapsedtime = omp_get_wtime() - starttime;
			// report elapsed time
			/*printf("Time Elapsed: %f Secs \n",
				elapsedtime);*/
			average_elapsedtime += elapsedtime;
			average_all_elapsedtime += elapsedtime;

#pragma omp parallel for
			for (int i = 0; i < N; i++)
			{
				for (int j = 0; j < N; j++)
				{
					matrix[i][j] = copy_matrix[i][j];
					L[i][j] = 0;
					U[i][j] = 0;
				}

			}
#pragma omp parallel for 
		for (int i = 0; i < N; i++) {
			L[i][i] = 1;
		}
		}

		/*printf("Average Time Elapsed: %f Secs \n",
			(average_elapsedtime / epoch));*/

		// write inputted data into the file.
		outfile << det_u << endl;
		free(matrix);
		free(L);
		free(U);
	}
	printf("Total Average Time Elapsed: %f Secs \n",
		(average_all_elapsedtime / (epoch*num_of_files)));
	return 0;

}