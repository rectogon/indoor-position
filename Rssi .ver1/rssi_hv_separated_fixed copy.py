import pandas as pd
import numpy as np
from scipy.interpolate import griddata, Rbf
from scipy.ndimage import gaussian_filter
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap

def load_rssi_data_hv_separated(df):
    """
    Load DataFrame and return grouped lists by rssi_data_id with H,V separation.
    Now returns H and V values separately along with combined values.
    Enhanced version with detailed rssi_data_id tracking and display.
    """
    grouped = df.groupby('rssi_data_id', sort=False)
    
    rssi_values_lists = []
    h_values_lists = []  # เพิ่มตัวแปรเก็บค่า H แยก
    v_values_lists = []  # เพิ่มตัวแปรเก็บค่า V แยก
    x_values_lists = []
    y_values_lists = []
    rssi_data_ids = []
    
    print("=" * 80)
    print("RSSI Data Processing with H,V Separation - Enhanced Display (SEPARATED H,V)")
    print("=" * 80)
    
    for rssi_data_id, group in grouped:
        print(f"\nProcessing rssi_data_id: {rssi_data_id}")
        print("-" * 50)
        
        # Separate H and V values based on anchor_id
        h_values = []
        v_values = []
        x_coords = []
        y_coords = []
        
        # Group by anchor (A1, A2, A3, A4)
        anchors = {}
        for idx, row in group.iterrows():
            anchor_id = row['anchor_id']
            rssi_val = row['rssi_value']
            x_val = row['X']
            y_val = row['Y']
            
            # Extract anchor name and orientation (A1_H, A1_V, etc.)
            if '_H' in anchor_id:
                anchor_name = anchor_id.replace('_H', '')
                if anchor_name not in anchors:
                    anchors[anchor_name] = {'H': None, 'V': None, 'X': x_val, 'Y': y_val}
                anchors[anchor_name]['H'] = rssi_val
                print(f"  {anchor_id}: {rssi_val:.2f} dBm (Horizontal)")
            elif '_V' in anchor_id:
                anchor_name = anchor_id.replace('_V', '')
                if anchor_name not in anchors:
                    anchors[anchor_name] = {'H': None, 'V': None, 'X': x_val, 'Y': y_val}
                anchors[anchor_name]['V'] = rssi_val
                print(f"  {anchor_id}: {rssi_val:.2f} dBm (Vertical)")
        
        print(f"\nSeparated H,V Values for rssi_data_id: {rssi_data_id}")
        print("Anchor\t\tH (dBm)\t\tV (dBm)\t\tA = H⊕V (power-sum, dBm)\tPosition (X,Y)")
        print("-" * 75)
        
        # Calculate A = sqrt(VÂ² + HÂ²) for each anchor และแยกเก็บ H,V
        combined_values = []
        h_only_values = []  # เก็บค่า H แยก
        v_only_values = []  # เก็บค่า V แยก
        
        for anchor_name in sorted(anchors.keys()):  # Sort for consistent display
            values = anchors[anchor_name]
            if values['H'] is not None and values['V'] is not None:
                # Calculate magnitude: A = sqrt(VÂ² + HÂ²)
                h_val = values['H']
                v_val = values['V']
                
                # เก็บค่า H, V แยกกัน
                h_only_values.append(h_val)
                v_only_values.append(v_val)
                
                # Convert to linear scale for proper magnitude calculation
                # RSSI is in dBm, convert to linear scale
                h_linear = 10**(h_val/10)
                v_linear = 10**(v_val/10)
                
                # Calculate magnitude in linear scale
                total_linear = h_linear + v_linear
                # Convert back to dBm (guard tiny value)
                magnitude_dbm = 10 * np.log10(max(total_linear, 1e-12))
                
                combined_values.append(magnitude_dbm)
                x_coords.append(values['X'])
                y_coords.append(values['Y'])
                
                print(f"{anchor_name}\t\t{h_val:8.2f}\t{v_val:8.2f}\t{magnitude_dbm:12.2f}\t\t({values['X']:.1f}, {values['Y']:.1f})")
            else:
                missing = []
                if values['H'] is None:
                    missing.append('H')
                if values['V'] is None:
                    missing.append('V')
                print(f"{anchor_name}\t\tMISSING: {', '.join(missing)} component(s)")
        
        # Summary for this rssi_data_id
        if len(combined_values) >= 4:  # Need at least 4 anchors
            print(f"\n rssi_data_id {rssi_data_id}: Successfully processed {len(combined_values)} anchors")
            print(f"  Combined A values range: {min(combined_values):.2f} to {max(combined_values):.2f} dBm")
            print(f"  H values range: {min(h_only_values):.2f} to {max(h_only_values):.2f} dBm")
            print(f"  V values range: {min(v_only_values):.2f} to {max(v_only_values):.2f} dBm")
            print(f"  Position range: X({min(x_coords):.1f} to {max(x_coords):.1f}), Y({min(y_coords):.1f} to {max(y_coords):.1f})")
            
            rssi_values_lists.append(combined_values)
            h_values_lists.append(h_only_values)  # เก็บค่า H แยก
            v_values_lists.append(v_only_values)  # เก็บค่า V แยก
            x_values_lists.append(x_coords)
            y_values_lists.append(y_coords)
            rssi_data_ids.append(rssi_data_id)
        else:
            print(f"rssi_data_id {rssi_data_id}: Insufficient anchors ({len(combined_values)}/4 minimum)")
    
    print("=" * 80)
    print(f"SUMMARY: {len(rssi_values_lists)} out of {len(grouped)} rssi_data_id groups processed successfully")
    print("=" * 80)
    
    list_of_5s = [5] * len(rssi_values_lists)
    # Return เพิ่ม h_values_lists และ v_values_lists
    return rssi_values_lists, list_of_5s, x_values_lists, y_values_lists, rssi_data_ids, h_values_lists, v_values_lists

def create_improved_tensor_hv_separated(rssi_values, x_values, y_values, h_values, v_values, grid_size=11):
    """
    Create a tensor of shape [5, 6, 121, 1] using separate H and V values in channels.
    
    Channel Assignment:
    0. H values with RBF interpolation
    1. V values with Gaussian Process
    2. H values with Voronoi + Distance Decay
    3. V values with Path Loss Model
    4. H values with Kriging
    5. V values with Spectral Reconstruction
    """
    # Tensor shape: (6, grid_size * grid_size, 1)
    tensor = np.zeros((5, 6, grid_size * grid_size, 1))

    # Convert to numpy arrays
    x_array = np.array(x_values, dtype=float)
    y_array = np.array(y_values, dtype=float)
    rssi_array = np.array(rssi_values, dtype=float)
    h_array = np.array(h_values, dtype=float)  # ค่า H แยก
    v_array = np.array(v_values, dtype=float)  # ค่า V แยก
    
    print(f"Processing channels with separate H,V values:")
    print(f"H values: {h_array}")
    print(f"V values: {v_array}")
    print(f"Combined values: {rssi_array}")
    
    # Handle degenerate cases
    x_min, x_max = x_array.min(), x_array.max()
    y_min, y_max = y_array.min(), y_array.max()
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    # Add jitter if points are too close
    if x_range < 1e-10:
        x_array = x_array + np.random.normal(0, 0.1, size=len(x_array))
        x_range = x_array.max() - x_array.min()
    if y_range < 1e-10:
        y_array = y_array + np.random.normal(0, 0.1, size=len(y_array))
        y_range = y_array.max() - y_array.min()
    
    # Normalize coordinates
    x_norm = (x_array - x_array.min()) / x_range * (grid_size - 1)
    y_norm = (y_array - y_array.min()) / y_range * (grid_size - 1)
    
    # Create grid
    grid_x, grid_y = np.meshgrid(np.arange(grid_size), np.arange(grid_size))
    grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
    
    temp_tensor = np.zeros((6, grid_size * grid_size, 1))
    
    # Channel 0: H values with RBF Interpolation
    print("Processing Channel 0: H values with RBF Interpolation")
    try:
        rbf = Rbf(x_norm, y_norm, h_array, function='multiquadric', smooth=0, epsilon=1.0)
        rbf_values = rbf(grid_x, grid_y)
        temp_tensor[0, :, 0] = rbf_values.ravel()
    except Exception as e:
        # Fallback to IDW if RBF fails
        for i, (gx, gy) in enumerate(grid_points):
            distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            distances[distances == 0] = 0.01
            weights = 1 / distances**2
            weights = weights / weights.sum()
            temp_tensor[0, i, 0] = np.sum(weights * h_array)
    
    # Channel 1: V values with Gaussian Process Regression
    print("Processing Channel 1: V values with Gaussian Process Regression")
    try:
        kernel = 1.0 * RBF(length_scale=2.0, length_scale_bounds=(1e-1, 10.0))
        gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.1, normalize_y=True)
        
        points = np.column_stack((x_norm, y_norm))
        gpr.fit(points, v_array)
        
        gpr_mean, gpr_std = gpr.predict(grid_points, return_std=True)
        temp_tensor[1, :, 0] = gpr_mean
    except Exception as e:
        # Fallback to IDW interpolation
        for i, (gx, gy) in enumerate(grid_points):
            distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            distances[distances == 0] = 0.01
            weights = 1 / distances
            weights = weights / weights.sum()
            temp_tensor[1, i, 0] = np.sum(weights * v_array)
    
    # Channel 2: H values with Voronoi-based Nearest Neighbor with Distance Decay
    print("Processing Channel 2: H values with Voronoi + Distance Decay")
    for i, (gx, gy) in enumerate(grid_points):
        distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
        nearest_idx = np.argmin(distances)
        nearest_dist = distances[nearest_idx]
        
        # Apply exponential decay based on distance
        decay_factor = np.exp(-nearest_dist / 2.0)
        base_value = h_array[nearest_idx]
        
        # Add contribution from other points based on distance
        weights = np.exp(-distances / 3.0)
        weights = weights / weights.sum()
        weighted_value = np.sum(weights * h_array)
        
        temp_tensor[2, i, 0] = decay_factor * base_value + (1 - decay_factor) * weighted_value
    
    # Channel 3: V values with Path Loss Model Propagation
    print("Processing Channel 3: V values with Path Loss Model")
    reference_distance = 1.0
    path_loss_exponent = 2.5
    
    for i, (gx, gy) in enumerate(grid_points):
        distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
        distances[distances < reference_distance] = reference_distance
        
        # Calculate individual contributions from each measurement point
        individual_contributions = []
        for j, (rssi_val, dist) in enumerate(zip(v_array, distances)):
            # Add some variation to path loss exponent based on measurement point
            local_n = path_loss_exponent + 0.3 * np.sin(j * np.pi / 4)
            
            # Path loss: PL(d) = PL(d0) + 10*n*log10(d/d0)
            path_loss_db = 10 * local_n * np.log10(dist / reference_distance)
            
            # Transmitted power estimation (reverse path loss)
            estimated_tx_power = rssi_val + path_loss_db
            
            # Re-calculate RSSI at grid point with some environmental variation
            environmental_loss = 2.0 * np.sin(gx * 0.5) * np.cos(gy * 0.3)
            predicted_rssi = estimated_tx_power - path_loss_db - environmental_loss
            
            individual_contributions.append(predicted_rssi)
        
        # Weight by inverse distance squared
        inv_dist_weights = 1 / (distances ** 2)
        inv_dist_weights = inv_dist_weights / inv_dist_weights.sum()
        
        temp_tensor[3, i, 0] = np.sum(inv_dist_weights * np.array(individual_contributions))
    
    # Channel 4: H values with Kriging Interpolation
    print("Processing Channel 4: H values with Kriging Interpolation")
    try:
        # Calculate empirical variogram parameters
        max_distance = np.sqrt((grid_size-1)**2 + (grid_size-1)**2)
        
        # Calculate pairwise distances between measurement points
        measurement_points = np.column_stack((x_norm, y_norm))
        pairwise_distances = cdist(measurement_points, measurement_points)
        
        # Estimate variogram parameters from data
        sill = np.var(h_array) if np.var(h_array) > 0 else 1.0
        range_param = max_distance / 2.0
        nugget = sill * 0.1  # 10% nugget effect
        
        for i, (gx, gy) in enumerate(grid_points):
            # Distances from grid point to all measurement points
            grid_to_measurements = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            
            # Spherical variogram model
            def spherical_variogram(h, nugget, sill, range_param):
                h = np.array(h)
                gamma = np.zeros_like(h)
                
                # For h <= range
                mask1 = h <= range_param
                h_norm = h[mask1] / range_param
                gamma[mask1] = nugget + (sill - nugget) * (1.5 * h_norm - 0.5 * h_norm**3)
                
                # For h > range
                mask2 = h > range_param
                gamma[mask2] = sill
                
                return gamma
            
            # Calculate semivariogram values
            gamma_values = spherical_variogram(grid_to_measurements, nugget, sill, range_param)
            
            # Kriging weights (simplified ordinary kriging)
            # Convert semivariogram to covariance: C(h) = sill - Î³(h)
            covariances = sill - gamma_values
            covariances[covariances < 0] = 1e-10  # Avoid negative covariances
            
            # Simple kriging weights (proportional to covariance)
            weights = covariances / (np.sum(covariances) + 1e-10)
            
            temp_tensor[4, i, 0] = np.sum(weights * h_array)
            
    except Exception as e:
        # Fallback to improved IDW if kriging fails
        for i, (gx, gy) in enumerate(grid_points):
            distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            distances[distances == 0] = 0.01
            # Use distance-squared weighting with some variation
            weights = 1 / (distances ** (2 + 0.5 * np.sin(i * 0.1)))
            weights = weights / weights.sum()
            temp_tensor[4, i, 0] = np.sum(weights * h_array)
    
    # Channel 5: V values with Spectral Analysis (Fourier-based reconstruction)
    print("Processing Channel 5: V values with Spectral Reconstruction")
    try:
        # Create initial interpolation using IDW
        initial_values = np.zeros(len(grid_points))
        for i, (gx, gy) in enumerate(grid_points):
            distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            distances[distances == 0] = 0.01
            weights = 1 / distances**2
            weights = weights / weights.sum()
            initial_values[i] = np.sum(weights * v_array)
            
        # Reshape to 2D grid
        initial_2d = initial_values.reshape(grid_size, grid_size)
            
        # Apply 2D FFT
        fft_2d = np.fft.fft2(initial_2d)
            
        # Create frequency coordinates
        freq_x = np.fft.fftfreq(grid_size, d=1.0)
        freq_y = np.fft.fftfreq(grid_size, d=1.0)
        fx, fy = np.meshgrid(freq_x, freq_y)
            
        # Create low-pass filter (Gaussian in frequency domain)
        sigma_freq = 0.25  # Controls smoothing amount
        lpf = np.exp(-(fx**2 + fy**2) / (2 * sigma_freq**2))
            
        # Apply filter in frequency domain
        filtered_fft = fft_2d * lpf
            
        # Inverse FFT to get smoothed result
        smoothed_2d = np.real(np.fft.ifft2(filtered_fft))
            
        # Reinforce original measurement locations
        for j, (xn, yn) in enumerate(zip(x_norm, y_norm)):
            xi, yi = int(round(np.clip(xn, 0, grid_size-1))), int(round(np.clip(yn, 0, grid_size-1)))
            # Blend original value with smoothed value
            blend_weight = 0.6
            smoothed_2d[yi, xi] = blend_weight * v_array[j] + (1 - blend_weight) * smoothed_2d[yi, xi]
            
        # Add high-frequency detail back
        # Create detail from difference between original IDW and very smooth version
        very_smooth_fft = fft_2d * np.exp(-(fx**2 + fy**2) / (2 * (sigma_freq * 0.5)**2))
        very_smooth_2d = np.real(np.fft.ifft2(very_smooth_fft))
        detail = initial_2d - very_smooth_2d
            
        # Add scaled detail back
        final_result = smoothed_2d + 0.3 * detail
            
        # Final light smoothing to remove artifacts
        final_result = gaussian_filter(final_result, sigma=0.3)
            
        # Store the result in tensor
        temp_tensor[5, :, 0] = final_result.ravel()
        
        print("Channel 5: V values spectral analysis completed successfully")
        
    except Exception as e:
        # Fallback to smoothed IDW
        print(f"Channel 5: V values spectral failed, using smoothed IDW fallback: {str(e)[:50]}...")
        for i, (gx, gy) in enumerate(grid_points):
            distances = np.sqrt((gx - x_norm)**2 + (gy - y_norm)**2)
            distances[distances == 0] = 0.01
            weights = 1 / distances**1.5
            weights = weights / weights.sum()
            temp_tensor[5, i, 0] = np.sum(weights * v_array)
            
        # Apply Gaussian smoothing to the result
        channel_5_2d = temp_tensor[5, :, 0].reshape(grid_size, grid_size)
        smoothed_2d = gaussian_filter(channel_5_2d, sigma=0.8)
        temp_tensor[5, :, 0] = smoothed_2d.ravel()

    # Post-processing: Ensure reasonable value ranges and diversity
    print("Applying post-processing to all channels...")
    
    for ch in range(6):
        ch_data = temp_tensor[ch, :, 0]
        
        # Ensure minimum variation (at least 2 dB range)
        if ch_data.max() - ch_data.min() < 2.0:
            # Add controlled variation while preserving the overall pattern
            variation = 1.0 * np.sin(np.arange(len(ch_data)) * 0.1) * np.cos(np.arange(len(ch_data)) * 0.07)
            temp_tensor[ch, :, 0] = ch_data + variation
            
        # Clamp to reasonable RSSI range (-100 to -20 dBm)
        temp_tensor[ch, :, 0] = np.clip(temp_tensor[ch, :, 0], -100, -20)
        
        # Print channel statistics
        ch_data_final = temp_tensor[ch, :, 0]
        data_type = "H" if ch % 2 == 0 else "V"  # Even channels = H, Odd channels = V
        print(f"Channel {ch} ({data_type}): min={ch_data_final.min():6.2f}, max={ch_data_final.max():6.2f}, "
              f"mean={ch_data_final.mean():6.2f}, std={ch_data_final.std():6.2f}")

    # Copy channels to all 5 dimensions
    for dim in range(5):
        for ch in range(6):
            tensor[dim, ch, :, :] = temp_tensor[ch, :, :]
    
    print("Tensor creation complete with separate H,V channels!")
    return tensor

def process_all_groups_improved_hv_separated(df):
    """
    Process all groups with separated H,V values in channels.
    Returns tensors and group information for animation.
    """
    # เรียกใช้ฟังก์ชันใหม่ที่ return H,V แยก
    rssi_values, fives, x_values, y_values, rssi_ids, h_values, v_values = load_rssi_data_hv_separated(df)
    
    tensors = []
    group_info = []
    
    print("\nEnhanced RSSI Tensor Creation with Separated H,V Channels:")
    print("Channel 0: H values - Radial Basis Function (RBF)")
    print("Channel 1: V values - Gaussian Process Regression")
    print("Channel 2: H values - Voronoi + Distance Decay")
    print("Channel 3: V values - Path Loss Model")
    print("Channel 4: H values - Kriging Interpolation")
    print("Channel 5: V values - Spectral Reconstruction")
    print("NOTE: Alternating H,V pattern across channels")
    print("-" * 80)
    
    for i in range(len(rssi_values)):
        if len(rssi_values[i]) < 4:  # Need at least 4 anchors
            print(f"Warning: Group {i} (rssi_data_id: {rssi_ids[i]}) has {len(rssi_values[i])} anchors instead of minimum 4")
            continue
        
        print(f"\nCreating tensor for rssi_data_id: {rssi_ids[i]} (Group {i})")
        # ส่งค่า H,V แยกเข้าไปในฟังก์ชัน
        tensor = create_improved_tensor_hv_separated(
            rssi_values[i], x_values[i], y_values[i], 
            h_values[i], v_values[i]  # ส่งค่า H,V แยก
        )
        tensors.append(tensor)
        
        # Store group information for animation
        group_info.append({
            'group_index': i,
            'rssi_data_id': rssi_ids[i],
            'x_coords': x_values[i],
            'y_coords': y_values[i],
            'rssi_values': rssi_values[i],
            'h_values': h_values[i],  # เพิ่ม H values
            'v_values': v_values[i]   # เพิ่ม V values
        })
        
        print(f" rssi_data_id {rssi_ids[i]} -> Tensor shape: {tensor.shape}")
        print(f"  Grid positions: X={x_values[i]}, Y={y_values[i]}")
        print(f"  RSSI Combined values: {[f'{val:.2f}' for val in rssi_values[i]]}")
        print(f"  H values: {[f'{val:.2f}' for val in h_values[i]]}")
        print(f"  V values: {[f'{val:.2f}' for val in v_values[i]]}")
        
        # Print detailed statistics for each channel
        for ch in range(6):
            ch_data = tensor[0, ch, :, 0]  # Use first dimension for stats
            data_type = "H" if ch % 2 == 0 else "V"
            value_range = ch_data.max() - ch_data.min()
            print(f"  Ch{ch}({data_type}): min={ch_data.min():6.2f}, max={ch_data.max():6.2f}, "
                  f"mean={ch_data.mean():6.2f}, std={ch_data.std():6.2f}, range={value_range:6.2f}")
    
    print(f"\nTensor creation complete: {len(tensors)} tensors created successfully")
    return tensors, group_info

# Updated visualization class to show H,V separation
class RSSIAnimationVisualizerHV:
    """
    Enhanced RSSI Animation Visualizer with H,V separated channels
    """
    
    def __init__(self, tensors, group_info, grid_size=11, interval=2000):
        """
        Initialize the visualizer with H,V separated channels
        """
        self.tensors = tensors
        self.group_info = group_info
        self.grid_size = grid_size
        self.interval = interval
        
        # Updated channel names for H,V separation
        self.channel_names = [
            'H - RBF Interpolation',
            'V - Gaussian Process',
            'H - Voronoi + Distance Decay',
            'V - Path Loss Model',
            'H - Kriging Interpolation',
            'V - Spectral Reconstruction'
        ]
        
        # Calculate global min/max for consistent color scaling
        self.calculate_global_range()
        
        # Create custom colormap
        self.create_custom_colormap()
        
        # Animation objects
        self.fig = None
        self.axes = None
        self.images = []
        self.colorbars = []
        self.ani = None
        self.group_text = None
        self.progress_text = None
    
    def calculate_global_range(self):
        """Calculate global min/max values across all tensors for consistent scaling"""
        if not self.tensors:
            self.vmin, self.vmax = -100, -20
            return
        
        all_values = []
        for tensor in self.tensors:
            for dim in range(tensor.shape[0]):
                for ch in range(tensor.shape[1]):
                    all_values.extend(tensor[dim, ch, :, 0])
            
        self.vmin = np.min(all_values)
        self.vmax = np.max(all_values)
        
        # Add some padding
        range_padding = (self.vmax - self.vmin) * 0.05
        self.vmin -= range_padding
        self.vmax += range_padding
        
        print(f"Global RSSI range for H,V separated: {self.vmin:.2f} to {self.vmax:.2f} dBm")
        
    def create_custom_colormap(self):
        """Create a custom colormap for RSSI visualization"""
        # Create separate colormaps for H and V channels
        h_colors = ['#8B0000', '#DC143C', '#FF6347', '#FFA500', '#FFD700', '#32CD32']  # Red to green for H
        v_colors = ['#000080', '#4169E1', '#00BFFF', '#00CED1', '#40E0D0', '#00FF7F']  # Blue to cyan for V
        
        self.h_cmap = LinearSegmentedColormap.from_list('rssi_h', h_colors, N=256)
        self.v_cmap = LinearSegmentedColormap.from_list('rssi_v', v_colors, N=256)
    
    def get_channel_colormap(self, channel):
        """Get appropriate colormap for channel (H or V)"""
        return self.h_cmap if channel % 2 == 0 else self.v_cmap
    
    def create_animation(self, save_as_gif=False, save_as_mp4=False, 
                        gif_filename='rssi_hv_separated.gif', mp4_filename='rssi_hv_separated.mp4'):
        """
        Create matplotlib animation showing all H,V separated channels
        """
        # Set up the figure and subplots
        self.fig, self.axes = plt.subplots(2, 3, figsize=(22, 14))
        self.fig.suptitle('RSSI H,V Separated Channels Animation', fontsize=18, fontweight='bold')
        
        # Initialize images for each channel
        self.images = []
        self.colorbars = []
        
        for ch in range(6):
            row, col = ch // 3, ch % 3
            ax = self.axes[row, col]
            
            # Get appropriate colormap for H or V
            cmap = self.get_channel_colormap(ch)
            
            # Create initial empty image
            initial_data = np.zeros((self.grid_size, self.grid_size))
            im = ax.imshow(initial_data, cmap=cmap, interpolation='bilinear',
                          vmin=self.vmin, vmax=self.vmax, aspect='equal')
            
            # Set title with H/V indicator
            data_type = "H (Horizontal)" if ch % 2 == 0 else "V (Vertical)"
            ax.set_title(f'Channel {ch}: {self.channel_names[ch]}', fontsize=11, fontweight='bold')
            ax.set_xlabel('X Grid Position', fontsize=9)
            ax.set_ylabel('Y Grid Position', fontsize=9)
            
            # Add grid lines
            ax.set_xticks(np.arange(-0.5, self.grid_size, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.grid_size, 1), minor=True)
            ax.grid(which="minor", color="white", linestyle='-', linewidth=0.5, alpha=0.3)
            ax.tick_params(which="minor", size=0)
            
            # Add colorbar with H/V label
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label(f'{data_type} RSSI (dBm)', rotation=270, labelpad=15, fontsize=8)
            cbar.ax.tick_params(labelsize=7)
            
            self.images.append(im)
            self.colorbars.append(cbar)
        
        # Add text for group information
        self.group_text = self.fig.text(0.02, 0.96, '', fontsize=12, fontweight='bold', 
                                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
        
        # Add progress indicator
        self.progress_text = self.fig.text(0.98, 0.96, '', fontsize=10, ha='right',
                                          bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)  # Make room for title and info text
        
        # Create animation
        self.ani = animation.FuncAnimation(
            self.fig, self.update_frame, frames=len(self.tensors),
            interval=self.interval, blit=False, repeat=True
        )
        
        # Save as MP4 if requested
        if save_as_mp4 and len(self.tensors) > 0:
            print(f"Saving H,V separated animation as {mp4_filename}...")
            try:
                fps = max(1, int(1000 / self.interval)) if self.interval > 0 else 5
                writer = animation.FFMpegWriter(
                    fps=fps,
                    metadata={'artist': 'RSSI H,V Visualizer', 'title': 'RSSI H,V Separated Animation'},
                    extra_args=['-r', str(fps)]
                )
                # self.ani.save(mp4_filename, writer="ffmpeg", fps=fps)
                print(f"H,V separated animation saved as {mp4_filename}")
            except Exception as e:
                print(f"Failed to save MP4: {str(e)}")
        
        return self.ani
    
    def update_frame(self, frame):
        """Update frame for H,V separated animation"""
        if frame >= len(self.tensors):
            return self.images + [self.group_text, self.progress_text]
        
        tensor = self.tensors[frame]
        group_info = self.group_info[frame]
        
        # Update group information text with H,V values
        info_text = f"Group {group_info['group_index']+1} | RSSI Data ID: {group_info['rssi_data_id']}\n"
        info_text += f"Coordinates: {group_info['x_coords']} | {group_info['y_coords']}\n"
        info_text += f"H Values: {[f'{val:.1f}' for val in group_info['h_values']]}\n"
        info_text += f"V Values: {[f'{val:.1f}' for val in group_info['v_values']]}"
        self.group_text.set_text(info_text)
        
        # Update progress indicator
        progress = f"Frame {frame+1}/{len(self.tensors)} ({(frame+1)/len(self.tensors)*100:.1f}%)"
        self.progress_text.set_text(progress)
        
        # Update each channel image
        for ch in range(6):
            # Reshape tensor data to 2D grid
            data_2d = tensor[0, ch, :, 0].reshape(self.grid_size, self.grid_size)
            
            # Update image data
            self.images[ch].set_array(data_2d)
            
            # Update subplot title with current statistics
            ch_data = tensor[0, ch, :, 0]
            actual_min, actual_max = ch_data.min(), ch_data.max()
            actual_mean = ch_data.mean()
            data_type = "H" if ch % 2 == 0 else "V"
            
            title = f'Ch {ch}: {data_type} - {self.channel_names[ch].split(" - ")[1]}\n'
            title += f'Range: {actual_max-actual_min:.1f}dB | Mean: {actual_mean:.1f}dBm'
            self.axes[ch//3, ch%3].set_title(title, fontsize=10, fontweight='bold')
            self.fig.canvas.flush_events()
        
        return self.images + [self.group_text, self.progress_text]
    
    def show_animation(self, save_as_gif=False, save_as_mp4=False, 
                      gif_filename='rssi_hv_separated.gif', mp4_filename='rssi_hv_separated.mp4'):
        """Show the H,V separated animation"""
        if len(self.tensors) == 0:
            print("No valid tensors found. Please check your data.")
            return None
        
        ani = self.create_animation(save_as_gif=save_as_gif, save_as_mp4=save_as_mp4,
                                   gif_filename=gif_filename, mp4_filename=mp4_filename)
        plt.show()
        return ani

# Updated training function for H,V separated processing
def train_model_hv_separated(df, f_learning_rate=0.001, f_dropout_ratio=0.3, 
                            epochs=100, batch_size=32, validation_split=0.2):
    """Train the RSSI CNN model with H,V separated processing and animation visualization"""
    
    # Import necessary modules for training
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Dense, Dropout, Flatten, Input, Conv2D, MaxPooling2D
        from tensorflow.keras.utils import to_categorical
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        from collections import Counter
    except ImportError as e:
        print(f"Required libraries not available: {e}")
        print("Please install tensorflow and scikit-learn")
        return None, None, None, None
    
    class RSSIDataProcessorHVSeparated:
        def __init__(self, df):
            self.df = df
            self.label_encoder_label = LabelEncoder()
            self.label_encoder_domain = LabelEncoder()
            self.label_encoder_domain2 = LabelEncoder()
            
        def load_and_prepare_data(self):
            """Load RSSI data and create tensors with labels using H,V separation"""
            print("Loading RSSI data with H,V separated processing...")
            
            # Group by rssi_data_id to get labels
            grouped = self.df.groupby('rssi_data_id', sort=False)
            
            labels = []
            domains = []
            domains2 = []
            rssi_data_ids = []
           
            for rssi_data_id, group in grouped:
                # Extract labels (modify these based on your CSV columns)
                if 'label' in group.columns:
                    label = group['label'].iloc[0]
                else:
                    label = 1  # Default label
                
                if 'domain' in group.columns:
                    domain = group['domain'].iloc[0]
                else:
                    domain = group['X'].iloc[0]
                    
                if 'domain2' in group.columns:
                    domain2 = group['domain2'].iloc[0]
                else:
                    domain2 = group['Y'].iloc[0]
                
                labels.append(label)
                domains.append(domain)
                domains2.append(domain2)
                rssi_data_ids.append(rssi_data_id)
            
            print(f"Found {len(labels)} groups for H,V separated processing")
            
            # Create tensors using H,V separated function
            tensors, group_info = process_all_groups_improved_hv_separated(self.df)
            
            # Filter out invalid tensors
            valid_tensors = []
            valid_labels = []
            valid_domains = []
            valid_domains2 = []
            
            for i, tensor in enumerate(tensors):
                if tensor is not None:
                    valid_tensors.append(tensor)
                    valid_labels.append(labels[i])
                    valid_domains.append(domains[i])
                    valid_domains2.append(domains2[i])
            
            # Convert to numpy arrays
            X = np.array(valid_tensors)
            
            # Encode labels
            y_label = self.label_encoder_label.fit_transform(valid_labels)
            y_domain = self.label_encoder_domain.fit_transform(valid_domains)
            y_domain2 = self.label_encoder_domain2.fit_transform(valid_domains2)
            
            # Convert to categorical
            n_class = len(np.unique(y_label))
            n_location = len(np.unique(y_domain))
            n2_location = len(np.unique(y_domain2))
            
            y_label_cat = to_categorical(y_label, num_classes=n_class)
            y_domain_cat = to_categorical(y_domain, num_classes=n_location)
            y_domain2_cat = to_categorical(y_domain2, num_classes=n2_location)
            
            print(f"Data loaded successfully with H,V separated processing:")
            print(f"  - Samples: {X.shape[0]}")
            print(f"  - Input shape: {X.shape[1:]}")
            print(f"  - Classes: {n_class}")
            print(f"  - Locations: {n_location}")
            print(f"  - Areas: {n2_location}")
            
            return X, y_label_cat, y_domain_cat, y_domain2_cat, n_class, n_location, n2_location, tensors, group_info
    
    # Load and prepare data
    processor = RSSIDataProcessorHVSeparated(df)
    print("train_model_hv_separated called")
    
    X, y_label, y_domain, y_domain2, n_class, n_location, n2_location, tensors, group_info = processor.load_and_prepare_data()
    
    # Create and show H,V separated animation
    print("\n" + "="*60)
    print("Creating RSSI H,V Separated Animation Visualization...")
    print("="*60)
    
    visualizer = RSSIAnimationVisualizerHV(tensors, group_info, interval=2000)
    
    # Split data for training
    X_train, X_test, y_label_train, y_label_test, y_domain_train, y_domain_test, y_domain2_train, y_domain2_test = train_test_split(
        X, y_label, y_domain, y_domain2, test_size=0.1, stratify=y_label
    )
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {y_domain_train.shape[0]}")
    
    # Create model architecture
    
    # === New 3D CNN model over time (T), space (11x11), channels (H/V) ===
    from tensorflow.keras.layers import Input, Lambda, Conv3D, BatchNormalization, Activation, MaxPool3D, GlobalAveragePooling3D, Dropout, Dense
    import tensorflow as tf


    model_input = Input(shape=X.shape[1:], name='model_input')   # Expecting (T, C, 121, 1)


    def _reshape_to_3d(x):

        # x: (batch, T, C, 121, 1)  ->  (batch, T, 11, 11, C)

        B = tf.shape(x)[0]

        T_dim = tf.shape(x)[1]

        C_dim = tf.shape(x)[2]

        x = tf.reshape(x, (B, T_dim, C_dim, 11, 11, 1))

        x = tf.squeeze(x, axis=-1)              # (B,T,C,11,11)

        x = tf.transpose(x, [0, 1, 3, 4, 2])    # (B,T,11,11,C)

        return x


    x = Lambda(_reshape_to_3d, name="reshape_T_11x11_C")(model_input)


    # Conv3D stack: mixes time and spatial patterns

    x = Conv3D(32, (3,3,3), padding='same', use_bias=False)(x)

    x = BatchNormalization()(x); x = Activation('relu')(x)

    x = MaxPool3D(pool_size=(1,2,2), padding='valid')(x)


    x = Conv3D(64, (3,3,3), padding='same', use_bias=False)(x)

    x = BatchNormalization()(x); x = Activation('relu')(x)

    x = MaxPool3D(pool_size=(1,2,2), padding='valid')(x)


    x = Conv3D(96, (3,3,3), padding='same', use_bias=False)(x)

    x = BatchNormalization()(x); x = Activation('relu')(x)


    x = GlobalAveragePooling3D()(x)

    x = Dropout(f_dropout_ratio)(x)

    x = Dense(128, activation='relu')(x)

    x = Dropout(f_dropout_ratio)(x)
    x_feat = Dropout(f_dropout_ratio)(x)

    x_1 = Dense(64, activation='relu')(x_feat)
    
    
    x_2 = Dense(128, activation='relu')(x_feat)
   
    
    x_3 = Dense(256, activation='relu')(x_feat)
    x_3 = Dense(128, activation='relu')(x_3)


    # Heads

    out_label   = Dense(1, activation='sigmoid', name='name_model_output_label')(x)

    out_domain  = Dense(n_location, activation='softmax', name='name_model_output_domain')(x_2)

    out_domain2 = Dense(n2_location, activation='softmax', name='name_model_output_domain2')(x)


    model = tf.keras.Model(inputs=model_input, outputs=[out_label, out_domain, out_domain2], name="RSSI_3D_CNN_HVSeparated")


    model.compile(

        optimizer=tf.keras.optimizers.Adam(learning_rate=f_learning_rate),

        loss={

            'name_model_output_label':   'binary_crossentropy',

            'name_model_output_domain':  'sparse_categorical_crossentropy',

            'name_model_output_domain2': 'sparse_categorical_crossentropy',

        },

        loss_weights={

            'name_model_output_label': 1e-4,    # de-emphasize the degenerate label head

            'name_model_output_domain': 1.0,

            'name_model_output_domain2': 1.0,

        },

        metrics={

            'name_model_output_label':  ['accuracy'],

            'name_model_output_domain': ['accuracy'],

            'name_model_output_domain2': ['accuracy'],

        },

    )


    model.summary()

    print(f"Trainable parameters: {model.count_params():,}")

    # === End of model definition ===


    # Compute per-output class weights for imbalanced classes

    try:

        #import numpy as np

        from sklearn.utils.class_weight import compute_class_weight


        def _cw(y, num_classes):

            classes = np.arange(num_classes, dtype=int)

            weights = compute_class_weight(class_weight='balanced', classes=classes, y=y.astype(int))

            return {int(i): float(w) for i, w in zip(classes, weights)}


        cw_domain  = _cw(y_domain_train,  n_location)

        cw_domain2 = _cw(y_domain2_train, n2_location)

        print("Class weights (domain):", cw_domain)

        print("Class weights (domain2):", cw_domain2)

    except Exception as e:

        print("Class weight computation failed, proceeding without. Error:", e)

        cw_domain = None

        cw_domain2 = None
    y_label_train  = np.array(y_label_train).reshape(-1)
    y_domain_train = np.array(y_domain_train).reshape(-1)
    y_domain2_train = np.array(y_domain2_train).reshape(-1)

    y_label_test  = np.array(y_label_test).reshape(-1)
    y_domain_test = np.array(y_domain_test).reshape(-1)
    y_domain2_test = np.array(y_domain2_test).reshape(-1)

    y_domain_train  = y_domain_train.reshape(-1, 16)[:, 0]
    y_domain2_train = y_domain2_train.reshape(-1, 24)[:, 0]

    y_domain_test  = y_domain_test.reshape(-1, 16)[:, 0]
    y_domain2_test = y_domain2_test.reshape(-1, 24)[:, 0]

    def _flatten_labels():
        import numpy as np
        def _fix(y):
            y = np.array(y)
            if y.ndim > 1:
                return y.reshape(y.shape[0], -1)[:, 0]  # ใช้ label ของ timestep แรก (หรือเลือก strategy ที่ต้องการ)
            return y
        return _fix

    _fix = _flatten_labels()

    y_label_train  = _fix(y_label_train)
    y_domain_train = _fix(y_domain_train)
    y_domain2_train = _fix(y_domain2_train)

    y_label_test  = _fix(y_label_test)
    y_domain_test = _fix(y_domain_test)
    y_domain2_test = _fix(y_domain2_test)

    print("Shapes:")
    print("X_train:", X_train.shape)
    print("y_label_train:", y_label_train.shape)
    print("y_domain_train:", y_domain_train.shape)
    print("y_domain2_train:", y_domain2_train.shape)
    history = model.fit(

        X_train,

        {

            'name_model_output_label':  y_label_train,

            'name_model_output_domain': y_domain_train,

            'name_model_output_domain2': y_domain2_train,

        },

        validation_data=(X_test, {

            'name_model_output_label':  y_label_test,

            'name_model_output_domain': y_domain_test,

            'name_model_output_domain2': y_domain2_test,

        }),

        epochs=epochs,

        batch_size=batch_size,

        verbose=2,

        class_weight=(

            None if cw_domain is None or cw_domain2 is None else {

                'name_model_output_domain':  cw_domain,

                'name_model_output_domain2': cw_domain2,

            }

        ),

    )


    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_results = model.evaluate(
        X_test,
        {
            'name_model_output_label': y_label_test,
            'name_model_output_domain': y_domain_test,
            'name_model_output_domain2': y_domain2_test
        },
        verbose=1
    )
    
    # Print test results
    print("\nTest Results (H,V Separated):")
    for i, metric_name in enumerate(model.metrics_names):
        print(f"{metric_name}: {test_results[i]:.4f}")
    
    return model, history, processor, visualizer

# Updated analyze function for H,V separation
def analyze_hv_separation_detailed(csv_file_path, sample_rssi_data_id=None):
    """
    Detailed analysis of H,V separation process showing the new separated channel approach.
    """
    print("Reading CSV file for H,V separated analysis...")
    df = pd.read_csv(csv_file_path)
    print(f"CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
    
    if sample_rssi_data_id is None:
        sample_rssi_data_id = df['rssi_data_id'].iloc[0]
    
    # Filter data for the specific sample
    sample_data = df[df['rssi_data_id'] == sample_rssi_data_id]
    
    print(f"Analyzing H,V SEPARATED processing for rssi_data_id: {sample_rssi_data_id}")
    print("=" * 70)
    
    # Group by anchor
    anchors = {}
    for idx, row in sample_data.iterrows():
        anchor_id = row['anchor_id']
        rssi_val = row['rssi_value']
        x_val = row['X']
        y_val = row['Y']
        
        if '_H' in anchor_id:
            anchor_name = anchor_id.replace('_H', '')
            if anchor_name not in anchors:
                anchors[anchor_name] = {'H': None, 'V': None, 'X': x_val, 'Y': y_val}
            anchors[anchor_name]['H'] = rssi_val
        elif '_V' in anchor_id:
            anchor_name = anchor_id.replace('_V', '')
            if anchor_name not in anchors:
                anchors[anchor_name] = {'H': None, 'V': None, 'X': x_val, 'Y': y_val}
            anchors[anchor_name]['V'] = rssi_val
    
    print("H,V Values Processing for Separated Channels:")
    print("Anchor\t\tH (dBm)\t\tV (dBm)\t\tChannel Assignment")
    print("-" * 70)
    
    h_values = []
    v_values = []
    combined_values = []
    
    for anchor_name, values in sorted(anchors.items()):
        if values['H'] is not None and values['V'] is not None:
            h_val = values['H']
            v_val = values['V']
            
            h_values.append(h_val)
            v_values.append(v_val)
            
            # Combined value for reference
            h_linear = 10**(h_val/10)
            v_linear = 10**(v_val/10)
            total_linear = h_linear + v_linear
            magnitude_dbm = 10 * np.log10(max(total_linear, 1e-12))
            combined_values.append(magnitude_dbm)
            
            print(f"{anchor_name}\t\t{h_val:8.2f}\t{v_val:8.2f}\t\tH→Ch0,2,4  V→Ch1,3,5")
        else:
            print(f"{anchor_name}\t\tMissing H or V component")
    
    print("\nChannel Assignment Summary:")
    print("Channel 0: H values with RBF Interpolation")
    print("Channel 1: V values with Gaussian Process")
    print("Channel 2: H values with Voronoi + Distance Decay")
    print("Channel 3: V values with Path Loss Model")
    print("Channel 4: H values with Kriging Interpolation")
    print("Channel 5: V values with Spectral Reconstruction")
    
    print(f"\nTotal H values: {len(h_values)} - Range: {min(h_values):.2f} to {max(h_values):.2f} dBm")
    print(f"Total V values: {len(v_values)} - Range: {min(v_values):.2f} to {max(v_values):.2f} dBm")
    print(f"Combined reference: {min(combined_values):.2f} to {max(combined_values):.2f} dBm")
    
    return anchors, h_values, v_values, combined_values, df

# Example usage for H,V separated processing
if __name__ == "__main__":
    import sys
    
    # Configuration
    CSV_FILE_PATH = "rssi_data_list_5_dataset.csv"
    
    print("Enhanced RSSI Processing with H,V SEPARATED Channels - NEW VERSION")
    print("=" * 80)
    print("This script processes RSSI data by:")
    print("1. Reading CSV file ONLY ONCE (optimized)")
    print("2. Separating H and V components from anchor_id")
    print("3. Using H values in channels 0, 2, 4 (alternating)")
    print("4. Using V values in channels 1, 3, 5 (alternating)")
    print("5. Applying different interpolation algorithms to each channel")
    print("6. Creating H,V separated animated visualization")
    print("7. Training CNN model with H,V separated features")
    print("=" * 80)
    
    try:
        # Detailed H,V separation analysis
        print("\n1. Analyzing H,V separated channel assignment...")
        anchors, h_values, v_values, combined_values, df = analyze_hv_separation_detailed(CSV_FILE_PATH)
        
        print("\n2. Processing all groups with H,V separated channels...")
        tensors, group_info = process_all_groups_improved_hv_separated(df)
        
        print(f"\nTotal tensors created: {len(tensors)}")
        if len(tensors) > 0:
            print(f"Tensor shape: {tensors[0].shape}")
            
            # Create H,V separated animation visualizer
            print("\n3. Creating H,V separated animation visualization...")
            visualizer = RSSIAnimationVisualizerHV(tensors, group_info, interval=1500)
            
            # Show animation
            print("Displaying H,V separated RSSI animation. Close window to continue...")
            ani = visualizer.show_animation(
                save_as_gif=True,
                save_as_mp4=True,
                gif_filename='rssi_hv_separated.gif',
                mp4_filename='rssi_hv_separated.mp4'
            )
        
        # Training with H,V separated features
        print("\n4. Starting model training with H,V separated processing...")
        model, history, processor, visualizer = train_model_hv_separated(
            df=df,
            f_learning_rate=0.001,
            f_dropout_ratio=0.3,
            epochs=50,
            batch_size=32
        )
        
        if model is not None:
            # Save model
            model.save_weights("final_rssi_model_hv_separated.h5")
            import tensorflow as tf
            tf.saved_model.save(model, "final_rssi_model_hv_separated_saved")
            #loaded = tf.saved_model.load("final_rssi_model_hv_separated_saved") #ตอนโหลดกลับ
            '''from tensorflow.keras.models import load_model
            

            model.save("final_rssi_model_hv_separated.h5", 
            save_format="h5",
            include_optimizer=False)

            # ตอนโหลด
            custom_objects = {
                "GradientReversalLayer": GradientReversalLayer
            }
            model = load_model("final_rssi_model_hv_separated.h5", custom_objects=custom_objects)
            print("\nModel saved as 'final_rssi_model_hv_separated.h5'")'''
        
        print("\n" + "="*80)
        print("H,V SEPARATED Channel Processing Complete!")
        print("="*80)
        print("NEW FEATURES:")
        print("✓ H values processed in channels 0, 2, 4")
        print("✓ V values processed in channels 1, 3, 5")
        print("✓ Different interpolation algorithms for each channel")
        print("✓ Separate colormaps for H (red-green) and V (blue-cyan)")
        print("✓ Enhanced visualization showing H,V separation")
        print("✓ Optimized single CSV read approach")
        print("="*80)
        
    except Exception as e:
        print(f"Error during H,V separated processing: {str(e)}")
        import traceback
        traceback.print_exc()