# KErnel OPerationS, on CPUs and GPUs, with autodiff and without memory overflows

```
          88           oooo    oooo             .oooooo.                                 88
        .8'`8.         `888   .8P'             d8P'  `Y8b                              .8'`8.
       .8'  `8.         888  d8'     .ooooo.  888      888 oo.ooooo.   .oooo.o        .8'  `8.
      .8'    `8.        88888[      d88' `88b 888      888  888' `88b d88(  "8       .8'    `8.
     .8'      `8.       888`88b.    888ooo888 888      888  888   888 `"Y88b.       .8'      `8.
    .8'        `8.      888  `88b.  888    .o `88b    d88'  888   888 o.  )88b     .8'        `8.
    88oooooooooo88     o888o  o888o `Y8bod8P'  `Y8bood8P'   888bod8P' 8""888P'     88oooooooooo88
                                                            888
                                                           o888o
```

**N.B.: This library is under development... some keys features have not been implemented yet.**

The KeOps library allows you to compute efficiently expressions of the form

```math
\alpha_i = \text{Reduction}_j \big[ f(x^1_i, x^2_i, ..., y^1_j, y^2_j, ...)  \big]
```

and their derivatives, where $`i`$ goes from $`1`$ to $`N`$ and $`j`$ from $`1`$ to $`M`$.

The basic example is the Gaussian convolution on a non regular grid in $`\mathbb R^3`$ (aka. **RBF kernel product**). Given :

- a target point cloud $`(x_i)_{i=1}^N \in  \mathbb R^{N \times 3}`$
- a source point cloud $`(y_j)_{j=1}^M \in  \mathbb R^{M \times 3}`$
- a signal or vector field $`(\beta_j)_{j=1}^M \in  \mathbb R^{M \times D}`$ attached to the $`y_j`$'s

KeOps allows you to compute efficiently the array $`(\alpha_i)_{i=1}^N \in  \mathbb R^{N \times D}`$ given by

```math
 \alpha_i =  \sum_j K(x_i,y_j) \beta_j,  \qquad i=1,\cdots,N
```

where $`K(x_i,y_j) = \exp(-\|x_i - y_j\|^2 / \sigma^2)`$.

The library comes with various examples ranging from lddmm (non rigid deformations) to kernel density estimations (non parametric statistics).
A **reference paper** will soon be put on Arxiv.

## Usage

We provide bindings in python (both numpy and pytorch complient),  Matlab and R.

In order to compute a fully differentiable torch Variable for the Gaussian-RBF kernel product,
one simply needs to type:

```python
import torch
from torch.autograd  import Variable
from pykeops.torch.kernels import Kernel, kernel_product

# Generate the data as pytorch Variables
x = Variable(torch.randn(100000,3), requires_grad=True)
y = Variable(torch.randn(200000,3), requires_grad=True)
b = Variable(torch.randn(200000,2), requires_grad=True)

# Pre-defined kernel: using custom expressions is also possible!
sigma  = Variable(Tensor([.5]))
params = {
    "id"      : Kernel("gaussian(x,y)"),
    "gamma"   : 1./sigma**2,
}

# Depending on the inputs' types, 'a' is a CPU or a GPU variable.
# It can be differentiated wrt. x, y, b and (soon!) sigma.
a = kernel_product( x, y, b, params)
```

We support:

- Summation and (numerically stable) LogSumExp reductions.
- User-defined formulas, using a simple string format (`"gaussian(x,y) * (1+linear(u,v)**2)"`) or a custom low-level syntax (`"Exp(-Cst(G)*SqDist(X,Y))"`).
- Simple syntax for kernels on feature spaces (say, locations+orientations varifold kernels in shape analysis).
- High-order derivatives.

In version 0.2, we will support:

- Derivatives with respect to the kernels' parameters.
- Non-radial kernels.

## Performances

In order to scale up on large datasets, we use a **tiled implementation** that allows us to get a $`O(N+M)`$ memory footprint instead of the usual $`O(NM)`$ codes generated by high level libraries - Thrust or cuda version of pyTorch and TensorFlow. CUDA kernels are compiled on-the-fly: one '.so' or '.dll' file is generated per mathematical expression, and can be re-used for other data samples and values of $`M`$ and $`N`$.

![Benchmark](./benchmark.png)

## Under the hood

As of today, KeOps provides two backends:

- a naive pytorch implementation, that can be used on small samples and for testing purposes.
- a homemade C++/CUDA engine, located in the [`./keops/core`](./keops/core) folder. Automatic differentiation of formulas is performed using variadic templating.

We're currently investigating the possibility of developing a third backend, that would rely on a genuine CUDA library such as [Tensor Comprehensions](http://facebookresearch.github.io/TensorComprehensions/introduction.html).

## Quick start

### Python users

Two steps:

1) Run the out-of-the-box working examples [`./pykeops/examples/convolution.py`](./pykeops/examples/convolution.py) and [`./pykeops/examples/generic_example.py`](./pykeops/examples/generic_example.py).

2) If you are already familiar with the LDDMM theory and want to get started quickly, please check the shapes toolboxes: [plmlab.math.cnrs.fr/jeanfeydy/shapes_toolbox](https://plmlab.math.cnrs.fr/jeanfeydy/shapes_toolbox) and [plmlab.math.cnrs.fr/jeanfeydy/lddmm_pytorch](https://plmlab.math.cnrs.fr/jeanfeydy/lddmm_pytorch).

### Matlab users

Two steps:

1) Compilation of the cuda codes. The subdirectory `./matlab` contains a shell script `makefile.sh`. The user needs to custom the paths contained in this file. The script produces mex files callable from any matlab script.

2) Run the out-of-the-box working examples `./matlab/example/convolution.m`

#### known issues

if an error involving libstdc++.so.6 occurs like

```
cmake: /usr/local/MATLAB/R2017b/sys/os/glnxa64/libstdc++.so.6: version `CXXABI_1.3.9' not found (required by cmake)
cmake: /usr/local/MATLAB/R2017b/sys/os/glnxa64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by cmake)
cmake: /usr/local/MATLAB/R2017b/sys/os/glnxa64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found (required by /usr/lib/x86_64-linux-gnu/libjsoncpp.so.1)
```

try to load matlab with the following linking variable :

```bash
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6;matlab
```

### R users

To do.

......
authors : [Benjamin Charlier](http://www.math.univ-montp2.fr/~charlier/), [Jean Feydy](http://www.math.ens.fr/~feydy/), [Joan Alexis Glaunès](http://www.mi.parisdescartes.fr/~glaunes/)
