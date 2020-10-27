# -*- coding: utf-8 -*-
# Written by Olga Moskvyak (olga.moskvyak@hdr.qut.edu.au)

import math
import os
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from skimage import transform
from utils.utils import unnormalize
from utils.data_manipulation import plot_image_coordinates
from core.evaluate import normalize_theta


def plot_images(
    input_images,
    coords_gt,
    coords_pred,
    theta_gt,
    theta_pred,
    prefix,
    output_dir,
    min_rows=2,
    max_cols=4,
    max_rows=4,
):
    """
    input_images: torch tensor of shape (bs, c, h, w)
    coords: torch tensor shape (bs, 5) where each row is [xc, yc, xt, yt, w]
    theta: torch tensor shape (bs) with values of theta
    file_name: string, name of the file to save plot
    max_cols: int, max number of columns in plot
    """
    images_un = unnormalize(input_images)
    bs = input_images.size(0)
    ncols = min(max_cols, bs)
    nrows = int(math.ceil(float(bs) / ncols))
    if nrows == 1:
        nrows = 2
        ncols = bs // nrows
    nrows = min(nrows, max_rows)

    fig, ax = plt.subplots(
        nrows=nrows, ncols=ncols * 2, figsize=(ncols * 2 * 4, nrows * 4)
    )
    for r in range(nrows):
        for c in range(ncols):
            # Plot grouhd truth
            if r * ncols + c >= bs:
                continue
            plot_image_coordinates(
                ax[r, 2 * c],
                images_un[r * ncols + c].numpy().transpose((1, 2, 0)),
                coords_gt[r * ncols + c, 0].numpy(),
                coords_gt[r * ncols + c, 1].numpy(),
                coords_gt[r * ncols + c, 2].numpy(),
                coords_gt[r * ncols + c, 3].numpy(),
                coords_gt[r * ncols + c, 4].numpy(),
            )
            ax[r, 2 * c].set_title(
                'GT Theta {:.0f} deg'.format(math.degrees(theta_gt[r * ncols + c]))
            )

            # Plot predictions
            plot_image_coordinates(
                ax[r, 2 * c + 1],
                images_un[r * ncols + c].numpy().transpose((1, 2, 0)),
                coords_pred[r * ncols + c, 0].numpy(),
                coords_pred[r * ncols + c, 1].numpy(),
                coords_pred[r * ncols + c, 2].numpy(),
                coords_pred[r * ncols + c, 3].numpy(),
                coords_pred[r * ncols + c, 4].numpy(),
            )
            ax[r, 2 * c + 1].set_title(
                'Preds Theta {:.0f} deg'.format(math.degrees(theta_pred[r * ncols + c]))
            )

    # Save plot
    file_name = os.path.join(output_dir, 'debug_images', '{}.png'.format(prefix))
    fig.savefig(file_name, format='png', dpi=100, bbox_inches='tight', facecolor='w')
    plt.close(fig)


def plot_rotated(
    input_images,
    coords_gt,
    coords_pred,
    theta_gt,
    theta_pred,
    prefix,
    output_dir,
    min_rows=2,
    max_cols=4,
    max_rows=4,
):
    """Plot images rotated with ground truth and predicted angles
    input_images: torch tensor of shape (bs, c, h, w)
    coords: torch tensor shape (bs, 5) where each row is [xc, yc, xt, yt, w]
    theta: torch tensor shape (bs) with values of theta
    file_name: string, name of the file to save plot
    max_cols: int, max number of columns in plot
    """
    images_un = unnormalize(input_images).numpy().transpose(0, 2, 3, 1)
    coords_gt = coords_gt.numpy()
    coords_pred = coords_pred.numpy()
    bs = input_images.size(0)
    ncols = min(max_cols, bs)
    nrows = int(math.ceil(float(bs) / ncols))
    if nrows == 1:
        nrows = 2
        ncols = bs // nrows
    nrows = min(nrows, max_rows)

    fig, ax = plt.subplots(
        nrows=nrows, ncols=ncols * 2, figsize=(ncols * 2 * 4, nrows * 4)
    )
    for r in range(nrows):
        for c in range(ncols):
            # Plot images rotated by grouhd truth
            if r * ncols + c >= bs:
                continue
            degrees_gt = math.degrees(theta_gt[r * ncols + c])
            image_rotated = transform.rotate(
                images_un[r * ncols + c],
                angle=degrees_gt,
                center=coords_gt[r * ncols + c, :1],
            )
            ax[r, 2 * c].imshow(image_rotated)
            ax[r, 2 * c].set_title('GT Rotated by {:.0f} deg'.format(degrees_gt))

            # Plot predictions
            degrees_pred = math.degrees(theta_pred[r * ncols + c])
            image_rotated = transform.rotate(
                images_un[r * ncols + c],
                angle=degrees_pred,
                center=coords_pred[r * ncols + c, :1],
            )
            ax[r, 2 * c + 1].imshow(image_rotated)
            ax[r, 2 * c + 1].set_title('Preds Rotated by {:.0f} deg'.format(degrees_pred))

    # Save plot
    file_name = os.path.join(output_dir, 'debug_images', '{}.png'.format(prefix))
    fig.savefig(file_name, format='png', dpi=100, bbox_inches='tight', facecolor='w')
    plt.close(fig)


def plot_images_theta(
    input_images,
    theta_gt,
    theta_pred,
    prefix,
    output_dir,
    min_rows=2,
    max_cols=4,
    max_rows=4,
):
    """
    input_images: torch tensor of shape (bs, c, h, w)
    theta_gt: torch tensor shape (bs, 1) with ground truth cosine values theta
    theta_pred: torch tensor shape (bs, 1) with predicted cosine values theta
    file_name: string, name of the file to save plot
    max_cols: int, max number of columns in plot
    """
    images_un = unnormalize(input_images)
    theta_gt = np.arccos(theta_gt.view(theta_gt.size(0)).numpy())
    theta_pred = np.arccos(theta_pred.view(theta_pred.size(0)).numpy())

    bs = input_images.size(0)
    ncols = min(max_cols, bs)
    nrows = int(math.ceil(float(bs) / ncols))
    if nrows == 1:
        nrows = 2
        ncols = bs // nrows
    nrows = min(nrows, max_rows)

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4, nrows * 4))
    for r in range(nrows):
        for c in range(ncols):
            ax[r, c].imshow(images_un[r * ncols + c].numpy().transpose((1, 2, 0)))
            ax[r, c].set_title(
                'Gt {:.0f} Pred {:.0f} deg'.format(
                    math.degrees(theta_gt[r * ncols + c]),
                    math.degrees(theta_pred[r * ncols + c]),
                )
            )

    # Save plot
    file_name = os.path.join(output_dir, 'debug_images', '{}.png'.format(prefix))
    fig.savefig(file_name, format='png', dpi=100, bbox_inches='tight', facecolor='w')
    plt.close(fig)


def plot_theta_err_hist(theta_gt, theta_pred, prefix, output_dir):
    np_norm_theta = np.vectorize(normalize_theta)
    theta_pred = np.rad2deg(theta_pred)
    theta_gt = np.rad2deg(theta_gt)
    err_theta = np.abs(np_norm_theta(theta_pred) - np_norm_theta(theta_gt))
    err_theta = np.abs(np_norm_theta(err_theta))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(err_theta,  bins=36)
    ax.set_xticks(list(range(0, 180, 10)))
    ax.set_xlabel('Error in degrees')
    ax.set_ylabel('Number of images')

    # Save plot
    file_name = os.path.join(output_dir, 'hist_{}.png'.format(prefix))
    fig.savefig(file_name, format='png', dpi=100, bbox_inches='tight', facecolor='w')
    plt.close(fig)