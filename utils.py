import cv2
import numpy as np

def upscale_and_sharpen(path, scale_factor=2, sharpen_amount=0.5, sharpen_radius=3):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    height, width = img.shape[:2]
    new_dimensions = (int(width * scale_factor), int(height * scale_factor))

    upscaled_img = cv2.resize(img, new_dimensions, interpolation=cv2.INTER_LANCZOS4)

    if len(upscaled_img.shape) == 2:
        upscaled_img = cv2.cvtColor(upscaled_img, cv2.COLOR_GRAY2BGR)

    gaussian_blur = cv2.GaussianBlur(upscaled_img, (0, 0), sharpen_radius)
    
    sharpened_img = cv2.addWeighted(upscaled_img, 1 + sharpen_amount, gaussian_blur, -sharpen_amount, 0)

    return sharpened_img

def method_1_simple_downscale_cv(i_ref: np.ndarray, ratio: float) -> np.ndarray:
    """
    Creates a low-resolution image by simple downscaling (degradation).
    
    Args:
        i_ref: The high-resolution reference image (NumPy array).
        ratio: The downscaling factor (e.g., 0.25 for 4x degradation).
    
    Returns:
        The degraded, low-resolution NumPy array.
    """
    if i_ref.size == 0:
        return np.array([])

    new_width = int(i_ref.shape[1] * ratio)
    new_height = int(i_ref.shape[0] * ratio)
    new_size = (new_width, new_height)
    
    print(f"I_ref size: {i_ref.shape[:2]} (HxW)")
    print(f"Method 1: Downscaling to {new_size} (WxH)")
    
    # Use cv2.INTER_CUBIC (Bicubic Interpolation) for downscaling. 
    # This is a common method that introduces the blurring/jaggies you want to correct.
    i_low = cv2.resize(i_ref, new_size, interpolation=cv2.INTER_CUBIC)
    
    return i_low

def method_2_realistic_degradation_cv(i_ref: np.ndarray, ratio: float, noise_std_dev: float = 10.0) -> np.ndarray:
    """
    Creates a more realistic low-resolution input by combining downscaling 
    with added Gaussian noise. (Note: JPEG compression in OpenCV is tricky 
    to simulate lossily without writing to disk; we focus on noise and blur).
    
    Args:
        i_ref: The high-resolution reference image (NumPy array).
        ratio: The downscaling factor.
        noise_std_dev: Standard deviation for Gaussian noise (0-255 scale).
        
    Returns:
        The degraded, low-resolution NumPy array with added noise.
    """
    # 1. Simple Downscale (Degradation)
    i_low_downscaled = method_1_simple_downscale_cv(i_ref, ratio)
    
    if i_low_downscaled.size == 0:
        return np.array([])
        
    print(f"Method 2: Adding Gaussian Noise (Std Dev={noise_std_dev})")

    # 2. Add Gaussian Noise (using floating point arithmetic for precision)
    
    # Convert image to float32 (0-255 scale)
    img_float = i_low_downscaled.astype(np.float32)
    
    # Generate Gaussian noise array (same shape as the image)
    noise = np.random.normal(0, noise_std_dev, img_float.shape).astype(np.float32)
    
    # Add noise
    noisy_img_float = img_float + noise
    
    # Clip and convert back to uint8 (0-255 scale)
    i_low_noisy = np.clip(noisy_img_float, 0, 255).astype(np.uint8)
    
    return i_low_noisy

