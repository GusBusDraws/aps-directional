# Standard library imports
from pathlib import Path
import imageio as iio
import numpy as np
import skimage


def get_imgs(
    img_dir_path, 
    img_start=None, 
    img_stop=None, 
    img_step=None, 
    n_imgs=None,
    print_nums=False,
    img_suffix='tif'
):
    """Load a specific range of images from a directory

    Parameters
    ----------
    img_dir_path : str or Path object
        Path of directory containing images.
    img_start : None or int, optional
        Starting index of images to preview, by default None.
    img_stop : None or int, optional
        Stopping index of images to preview, by default None.
    img_step : None or int, optional
        Step by which to retrieve images between img_start and img_stop, by default None
    img_suffix : str, optional
        File suffix of images in img_dir_path, by default 'tif'

    Returns
    -------
    np.array
        Numpy array with shape of NxHxW (N: number of images, H: height, W: width) representing images stacked along axis=0
    
    Raises
    ------
    ValueError
        Raised if img_dir_path does not exist 
    """
    # Convert img_dir_path to Path object if it is not one already
    img_dir_path = Path(img_dir_path)
    if not img_dir_path.is_dir():
        raise ValueError(f'Directory does not exist: {img_dir_path}')
    # Ensure img_suffix doesn't begin with a period
    if img_suffix[0] == '.':
        img_suffix = img_suffix[1:]
    # Make list of paths to images in director located at img_dir_path
    img_paths = [img_path for img_path in img_dir_path.glob(f'*.{img_suffix}')]
    img_paths.sort()
    if img_start is None:
        img_start = 0
    if img_stop is None:
        img_stop = len(img_paths)
    if n_imgs is not None:
        img_step = round((img_stop - img_start) / n_imgs)
    elif img_step is None:
        img_step = 1
    img_nums = np.arange(img_start, img_stop, img_step)
    print(f'Loading {len(img_nums)} images...')
    imgs = [iio.imread(img_paths[n]) for n in img_nums]
    if print_nums:
        img_map = [f'{i}: {img_n}' for i, img_n in enumerate(img_nums)]
        print('Images loaded:')
        print(img_map)
    else:
        print('Images loaded.')
    return np.stack(imgs, axis=0)

def save_as_gif(
    save_path, 
    imgs,
    equalize_hist=False,
    fps=10,
):
    """Function for saving image stack as an animated GIF

    Parameters
    ----------
    save_path : str or Path object
        Path to save animation, including filename. '.gif' will be to the end if it's not included
    imgs : np.ndarray
        NxHxD Numpy array (N: number of images, H: height, W: width) representing stack of images to be animated
    equalize_hist : bool, optional
        If True, adaptive histogram equaliztion performed on each frame of image to improve contrast. Defaults to False.
    fps : int, optional
        The framerate in frames per second to save the output GIF. Defaults to 10.

    Raises
    ------
    ValueError
        Raised if save_path already exists (to prevent accidental overwriting)
    """
    # If save_path doesn't end with '.gif', add it to the end
    save_path = str(save_path)
    if not save_path.endswith('.gif'):
        save_path = save_path + '.gif'
    # Convert save_path to a Path object
    save_path = Path(save_path)
    # Raise ValueError if save_path already exists (to prevent accidentally overwriting)
    if save_path.exists():
        raise ValueError(f'File already exists: {save_path}')
    print('Saving animation...')
    # Add each slice of imgs to a list of images
    img_list = [imgs[i, :, :] for i in range(imgs.shape[0])]
    # Iterate through images in list
    for i, img in enumerate(img_list):
        if equalize_hist:
            img = skimage.exposure.equalize_adapthist(img)
        img = skimage.util.img_as_ubyte(img)
        img_list[i] = img
    # Save list of images as frames in GIF
    iio.mimsave(save_path, img_list, fps=fps)
    print(f'Animation saved: {save_path}')