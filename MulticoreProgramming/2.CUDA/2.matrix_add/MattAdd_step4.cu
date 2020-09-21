#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include<stdlib.h>
#include <stdio.h>

struct threadInfo
{
	int globalThread;
	int block;
	int warp;
	int thread;
};

cudaError_t printWithCuda(threadInfo *t, unsigned int numOfBlock, unsigned int block_size);
void printThreadInfo(threadInfo * t, int size);

__global__ void printKernel(threadInfo *t)
{
	int globalThread = threadIdx.x + blockIdx.x * blockDim.x;
	int warp = threadIdx.x / warpSize;
	t[globalThread] = { globalThread, blockIdx.x, warp, threadIdx.x };

}

int main()
{
	const int numOfBlock = 2;
	const int block_size = 64;
	int size = numOfBlock * block_size;
	cudaEvent_t start;
	cudaEventCreate(&start);
	cudaEvent_t stop;
	cudaEventCreate(&stop);

	threadInfo *t = (threadInfo*)malloc(sizeof(threadInfo) * size);

	cudaEventRecord(start, NULL);

	// Print vectors in parallel.
	cudaError_t cudaStatus = printWithCuda(t, numOfBlock, block_size);
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "addWithCuda failed!");
		return 1;
	}

	// Print Threads info
	printThreadInfo(t, size);

	cudaEventRecord(stop, NULL);

	cudaStatus = cudaEventSynchronize(stop);
	float msecTotal = 0.0f;
	cudaStatus = cudaEventElapsedTime(&msecTotal, start, stop);

	fprintf(stderr, "Elapsed Time is %f ms \n", msecTotal);

	// cudaDeviceReset must be called before exiting in order for profiling and
	// tracing tools such as Nsight and Visual Profiler to show complete traces.
	cudaStatus = cudaDeviceReset();
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "cudaDeviceReset failed!");
		return 1;
	}

	return 0;
}

void printThreadInfo(threadInfo * t, int size) {
	for (int i = 0; i < size; i++)
	{
		printf("Calculated Thread: %d - Block: %d - Warp: %d - Thread: %d \n", t[i].globalThread, t[i].block, t[i].warp, t[i].thread);
	}

}

// Helper function for using CUDA to add vectors in parallel.
cudaError_t printWithCuda(threadInfo *t, unsigned int numOfBlock, unsigned int block_size)
{
	threadInfo *dev_t;
	cudaError_t cudaStatus;
	const int size = numOfBlock * block_size;
	// Choose which GPU to run on, change this on a multi-GPU system.
	cudaStatus = cudaSetDevice(0);
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "cudaSetDevice failed!  Do you have a CUDA-capable GPU installed?");
		goto Error;
	}

	// Allocate GPU buffers for three vectors (two input, one output)    .
	cudaStatus = cudaMalloc((void**)&dev_t, size * sizeof(threadInfo));
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "cudaMalloc failed!");
		goto Error;
	}

	// Launch a kernel on the GPU with one thread for each element.
	printKernel << < numOfBlock, block_size >> > (dev_t);

	// Check for any errors launching the kernel
	cudaStatus = cudaGetLastError();
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "addKernel launch failed: %s\n", cudaGetErrorString(cudaStatus));
		goto Error;
	}


	// cudaDeviceSynchronize waits for the kernel to finish, and returns
	// any errors encountered during the launch.
	cudaStatus = cudaDeviceSynchronize();
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "cudaDeviceSynchronize returned error code %d after launching addKernel!\n", cudaStatus);
		goto Error;
	}

	// Copy output vector from GPU buffer to host memory.
	cudaStatus = cudaMemcpy(t, dev_t, size * sizeof(threadInfo), cudaMemcpyDeviceToHost);
	if (cudaStatus != cudaSuccess) {
		fprintf(stderr, "cudaMemcpy failed!");
		goto Error;
	}

Error:
	cudaFree(dev_t);

	return cudaStatus;
}
