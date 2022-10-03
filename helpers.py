# Standard library imports
from pathlib import Path
import imageio.v3 as iio
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np
from skimage import exposure, filters, registration, util


def align_and_sub_liq(imgs, clip=[0.1, 99.9], hist_eq_clip_lim=0.0001):
    # Median filter images before converting to float
    print('Applying median filter...')
    imgs_med = filters.median(imgs)
    # Convert image to float before calculations
    imgs_float = util.img_as_float(imgs_med)
    # Calculate max offset between first and last image
    print('Calculating max offset between first and last images...')
    offset, error, diffphase = registration.phase_cross_correlation(
            imgs_float[0, :, :], imgs_float[-1, :, :])
    max_offset_r = int(offset[0])
    max_offset_c = int(offset[1])
    # Calc liquid-subtracted images with offset/drift-correction
    imgs_crctd = np.zeros(
            (imgs_float.shape[0],
             imgs_float.shape[1] - abs(max_offset_r),
             imgs_float.shape[2] - abs(max_offset_c)))
    # Iterate through each image and perform subtraction adjusting for offset
    print('Aligning each image and subtracting liquid image...')
    for i in range(imgs_float.shape[0]):
        offset, error, diffphase = registration.phase_cross_correlation(
                imgs_float[0, :, :], imgs_float[i, :, :])
        offset_r = int(offset[0])
        offset_c = int(offset[1])
        img_liq = imgs_float[
                0,
                : imgs_float.shape[1] - abs(max_offset_r),
                : imgs_float.shape[2] - abs(max_offset_c)]
        img_i = imgs_float[
                i,
                abs(offset_r) :
                        imgs.shape[1] - (abs(max_offset_r) - abs(offset_r)),
                abs(offset_c) :
                        imgs.shape[2] - (abs(max_offset_c) - abs(offset_c))]
        imgs_crctd[i, :, :] = img_i - img_liq
    if clip is not None:
        print('Clipping highest and lowest intensities...')
        low, high = np.percentile(imgs_crctd, (clip[0], clip[1]))
        imgs_crctd = np.clip(imgs_crctd, low, high)
    if hist_eq_clip_lim:
        print('Equalizing histograms...')
        imgs_sub_0to1 = exposure.rescale_intensity(
                imgs_crctd, in_range='image', out_range=(0, 1))
        imgs_crctd = exposure.equalize_adapthist(
                imgs_sub_0to1, clip_limit=hist_eq_clip_lim)
    print(f'{imgs_crctd.shape[0]} images processed.')
    return imgs_crctd

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
        Step by which to retrieve images between img_start and img_stop.
        Defaults to None
    img_suffix : str, optional
        File suffix of images in img_dir_path, by default 'tif'

    Returns
    -------
    np.array
        Numpy array with shape of NxHxW (N: number of images, H: height,
        W: width) representing images stacked along axis=0

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
        Path to save animation, including filename. '.gif' will be to the end
        if it's not included
    imgs : np.ndarray
        NxHxD Numpy array (N: number of images, H: height, W: width)
        representing stack of images to be animated
    equalize_hist : bool, optional
        If True, adaptive histogram equaliztion performed on each frame of
        image to improve contrast. Defaults to False.
    fps : int, optional
        The framerate in frames per second to save the output GIF.
        Defaults to 10.

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
    # Raise ValueError if save_path already exists
    # (to prevent accidentally overwriting)
    if save_path.exists():
        raise ValueError(f'File already exists: {save_path}')
    print('Saving animation...')
    # Add each slice of imgs to a list of images
    img_list = [imgs[i, :, :] for i in range(imgs.shape[0])]
    # Iterate through images in list
    for i, img in enumerate(img_list):
        if equalize_hist:
            img = exposure.equalize_adapthist(img)
        img = util.img_as_ubyte(img)
        img_list[i] = img
    # Save list of images as frames in GIF
    iio.mimsave(save_path, img_list, fps=fps)
    print(f'Animation saved: {save_path}')

def save_as_pngs(
        save_dir,
        imgs,
        scalebar_dict=dict(
                dx=1.4, units="um", length_fraction=0.2,
                border_pad=0.5, location='lower right'),
        timestamp_dict=dict(
                x=25, y=50, fps=0.8459, digits_before_dec=3,
                digits_after_dec=3)):
    save_dir = Path(save_dir)
    if not save_dir.is_dir():
        save_dir.mkdir(parents=True)
    else:
        raise ValueError(f'Directory already exists: {save_dir}')
    exp_name = save_dir.stem
    n_imgs = imgs.shape[0]
    n_digits = len(str(n_imgs))
    print('Saving images...')
    for i in range(n_imgs):
        save_path = Path(save_dir) / f'{exp_name}_{str(i).zfill(n_digits)}.png'
        if scalebar_dict is not None or timestamp_dict is not None:
            fig, ax = plt.subplots(dpi=300)
            ax.imshow(imgs[i, :, :], vmin=0, vmax=1, cmap='gray')
            ax.set_axis_off()
            if scalebar_dict is not None:
                # Create scale bar
                scalebar = ScaleBar(**scalebar_dict)
                ax.add_artist(scalebar)
            if timestamp_dict is not None:
                # Create timestamp
                timestamp_val = format(
                        i / timestamp_dict['fps'],
                        f".{timestamp_dict['digits_after_dec']}f")
                total_digits = (
                        1 + timestamp_dict['digits_after_dec']
                        + timestamp_dict['digits_before_dec'])
                timestamp_str = (
                        f'{str(timestamp_val).zfill(total_digits)} s')
                ax.text(
                        timestamp_dict['x'], timestamp_dict['y'], timestamp_str,
                        ha="left", va="center", size=9,
                        bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="None"))
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            iio.imwrite(save_path, imgs[i, :, :])
    print(f'{i + 1} images saved to: {save_dir}')

