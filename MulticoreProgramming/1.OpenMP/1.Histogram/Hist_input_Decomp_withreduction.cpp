#include <stdio.h>
#include <math.h>
#include <omp.h>

const long int NUMOFDATA = 800000000;
#define NUMOFTHREAD 4
// input Data Decomposition
int main(void)
{
#ifndef _OPENMP
	printf("OpenMP is not supported, sorry!\n");
	getchar();
	return 0;
#endif

	int nthread, *hist;
	int hist_res[100] = { 0 };

	hist = (int *)malloc(NUMOFDATA * sizeof(int));

	double starttime, elapsedtime;
	// -----------------------------------------------------------------------
	omp_set_num_threads(NUMOFTHREAD);

	starttime = omp_get_wtime();
	
	// create data 
#pragma omp parallel for
	for (int i = 0; i < NUMOFDATA; i++) {
		hist[i] = rand() % 100;
	}

#pragma omp parallel
	{
		int num;
		int id = omp_get_thread_num();

		nthread = omp_get_num_threads();

		// Mergae The Local Histograms after Calculation
		#pragma omp for reduction(+:hist_res[:100])  
		for (int i = 0; i < NUMOFDATA; i++) {
			num = hist[i];
			hist_res[num] ++;
		}

	}
	// get ending time and use it to determine elapsed time
	elapsedtime = omp_get_wtime() - starttime;
	// report elapsed time
	printf("Time Elapsed: %f Secs. \n",
		elapsedtime);
	printf("%d\n", NUMOFDATA);
	int count = 0;
	for (int i = 0; i < 100; i++) {
		count += hist_res[i];
	}
	printf("%d \n", count);


}