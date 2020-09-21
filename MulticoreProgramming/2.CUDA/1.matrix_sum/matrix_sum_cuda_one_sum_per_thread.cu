
#include "cuda_runtime.h"
#include "device_launch_parameters.h"

#include <stdio.h>
#include <cuda.h>

cudaError_t addWithCuda(int *c, const int *a, const int *b, unsigned int size);
void fillMat(int * v, int matSizeX, int matSizeY);
void printMat(int * v, int matSizeX, int matSizeY);

__global__ void addKernel(int *c, const int *a, const int *b, int size)
{
    int i = threadIdx.x + blockDim.x * blockIdx.x;

	if (i < size) {
		c[i] = a[i] + b[i];
	}
}


int main()
{
	const int matSizeX = 1000;
	const int matSizeY = 10000;
	const int arraySize = matSizeX*matSizeY;

	int * a;
	int * b;
	int * c;
	;
	a = (int*)malloc(sizeof(int)*matSizeX*matSizeY);
	b = (int*)malloc(sizeof(int)*matSizeX*matSizeY);
	c = (int*)malloc(sizeof(int)*matSizeX*matSizeY);
	fillMat(a, matSizeX, matSizeY);
	fillMat(b, matSizeX, matSizeY);
    // Add vectors in parallel.
    cudaError_t cudaStatus = addWithCuda(c, a, b, arraySize);
    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "addWithCuda failed!");
        return 1;
    }

	/*printMat(a, matSizeX, matSizeY);
	printMat(b, matSizeX, matSizeY);
	printMat(c, matSizeX, matSizeY);*/

    // cudaDeviceReset must be called before exiting in order for profiling and
    // tracing tools such as Nsight and Visual Profiler to show complete traces.
    cudaStatus = cudaDeviceReset();
    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaDeviceReset failed!");
        return 1;
    }

    return 0;
}

void fillMat(int * v, int matSizeX, int matSizeY) {
	static int L = 0;
	for (int i = 0; i < matSizeX; i++) {
		for (int j = 0; j < matSizeY; j++)
			v[i*matSizeY + j] = L++;
	}
}
void printMat(int * v, int matSizeX, int matSizeY) {
	int i;
	printf("[-] Vector elements: \n");
	for (int i = 0; i < matSizeX; i++) {
		for (int j = 0; j < matSizeY; j++)
			printf("%d ", v[i*matSizeY + j]);
		printf("\n");
	}
	printf("\b\b \n");
}

// Helper function for using CUDA to add vectors in parallel.
cudaError_t addWithCuda(int *c, const int *a, const int *b, unsigned int size)
{
    int *dev_a = 0;
    int *dev_b = 0;
    int *dev_c = 0;
    cudaError_t cudaStatus;

    // Choose which GPU to run on, change this on a multi-GPU system.
    cudaStatus = cudaSetDevice(0);
	//checkError(cudaStatus, 0);
    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaSetDevice failed!  Do you have a CUDA-capable GPU installed?");
        goto Error;
    }

    // Allocate GPU buffers for three vectors (two input, one output)    .
    cudaStatus = cudaMalloc((void**)&dev_c, size * sizeof(int));
	//checkError(cudaStatus, 1);
    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMalloc failed!");
        goto Error;
    }

    cudaStatus = cudaMalloc((void**)&dev_a, size * sizeof(int));

    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMalloc failed!");
        goto Error;
    }

    cudaStatus = cudaMalloc((void**)&dev_b, size * sizeof(int));

    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMalloc failed!");
        goto Error;
    }

    // Copy input vectors from host memory to GPU buffers.
    cudaStatus = cudaMemcpy(dev_a, a, size * sizeof(int), cudaMemcpyHostToDevice);

    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMemcpy failed!");
        goto Error;
    }

    cudaStatus = cudaMemcpy(dev_b, b, size * sizeof(int), cudaMemcpyHostToDevice);

    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMemcpy failed!");
        goto Error;
    }

	cudaEvent_t start;
	cudaEventCreate(&start);
	cudaEvent_t stop;
	cudaEventCreate(&stop);

	cudaEventRecord(start, NULL);
	int numOfThread = 1024;
	int n = int((size - 1) / numOfThread) + 1;
    // Launch a kernel on the GPU with one thread for each element.
    addKernel<<<n, numOfThread>>>(dev_c, dev_a, dev_b, size);

	cudaEventRecord(stop, NULL);
	cudaStatus = cudaEventSynchronize(stop);
	float msecTotal = 0.0f;
	cudaStatus = cudaEventElapsedTime(&msecTotal, start, stop);
	fprintf(stderr, "Elapsed Time is %f ms \n", msecTotal);

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
    cudaStatus = cudaMemcpy(c, dev_c, size * sizeof(int), cudaMemcpyDeviceToHost);

    if (cudaStatus != cudaSuccess) {
        fprintf(stderr, "cudaMemcpy failed!");
        goto Error;
    }

Error:
    cudaFree(dev_c);
    cudaFree(dev_a);
    cudaFree(dev_b);
    
    return cudaStatus;
}
