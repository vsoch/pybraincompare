'''
export.py: part of pybraincompare package
Functions to export images and data

'''

from builtins import range
def priors_to_brain_image(priors_df,output_name,mask_image):
    '''priors_to_brain_image
    Function to save brain images for each level of priors
    '''
    import numpy as np
    mask_image = nibabel.load(mask_image)
    roi = mask_image.get_data()
    
    # This will hold a 4D object for the data
    new_dim = mask_image.get_shape()
    new_dim = [new_dim[0],new_dim[1],new_dim[2],len(priors_df.columns)]
    data = np.zeros(shape=new_dim)
    for t in range(0,len(priors_df.columns)):
        thresh = priors_df.columns[t]
        new_image = np.zeros(shape=mask_image.get_shape())
        new_image[np.where(roi!=0)] = priors_df[thresh]
        data[:,:,:,t] = new_image
    final_img = nibabel.Nifti1Image(data, affine=mask_image.get_affine())
    final_img.set_filename("%s" %(output_name))
    nibabel.save(final_img,output_name)
