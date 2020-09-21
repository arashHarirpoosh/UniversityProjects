#include <fstream>
#include <iostream>
#include <omp.h>
#include <math.h>
using namespace std;

int findMandelbrot(double cr, double ci, int max_iterations)
{
	int i = 0;
	double zr = 0.0, zi = 0.0;
	while (i < max_iterations && zr * zr + zi * zi < 4.0)
	{
		double temp = zr * zr - zi * zi + cr;
		zi = 2.0 * zr * zi + ci;
		zr = temp;
		i++;
	}

	return i;
}

double mapToReal(int x, int imageWidth, double minR, double maxR)
{
	double range = maxR - minR;
	return x * (range / imageWidth) + minR;
}

double mapToImaginary(int y, int imageHeight, double minI, double maxI)
{
	double range = maxI - minI;
	return y * (range / imageHeight) + minI;
}

struct pixelChannels
{
	int r, g, b;
};

int main()
{
	const int imageWidth = 4000, imageHeight = 4000, maxN = 1024;
	double minR = -1.5, maxR = 0.7, minI = -1.0, maxI = 1.0;
	double elapsedtime, starttime, computational_elapsedtime;

	// Open the output file, write the PPM header...
	ofstream fout("output_image.ppm");
	fout << "P3" << endl; // "Magic Number" - PPM file
	fout << imageWidth << " " << imageHeight << endl; // Dimensions
	fout << "255" << endl; // Maximum value of a pixel R,G,B value...

	int x, y;

	starttime = omp_get_wtime();
	// For every pixel...
	omp_set_num_threads(4);

	pixelChannels *pc = (pixelChannels *)malloc(sizeof(pixelChannels)*imageWidth*imageHeight);

#pragma omp parallel
	{

#pragma omp for
		for (y = 0; y < imageHeight; y++) // Rows...
		{
#pragma omp task private(x) firstprivate(y) 
			{
				for (x = 0; x < imageWidth; x++) // Pixels in row (columns)...
				{

					// ... Find the real and imaginary values for c, corresponding to that
					//     x, y pixel in the image.

					int n;
					double cr = mapToReal(x, imageWidth, minR, maxR);
					double ci = mapToImaginary(y, imageHeight, minI, maxI);

					// ... Find the number of iterations in the Mandelbrot formula
					//     using said c.
					n = findMandelbrot(cr, ci, maxN);

					//struct pixelChannels p;
					int r, g, b;
					// ... Map the resulting number to an RGP value
					r = ((int)(n * sinf(n)) % 256);
					g = ((n * 3) % 256);
					b = (n % 256);


					pc[y*imageHeight + x] = { r,g,b };
				}
			}

		}

	}
	computational_elapsedtime += omp_get_wtime() - starttime;

	for (y = 0; y < imageHeight; y++) // Rows...
	{
		for (x = 0; x < imageWidth; x++) // Pixels in row (columns)...
		{
			struct pixelChannels p = pc[y*imageHeight + x];
			fout << p.r << " " << p.g << " " << p.b << " ";
		}
		fout << endl;
	}
	elapsedtime = omp_get_wtime() - starttime;
	// report elapsed time
	printf("Time Elapsed %f\n", elapsedtime);

	printf("Computational Elapsed %f \n", computational_elapsedtime);

	fout.close();

	cout << "Finished!" << endl;
	return 0;
}