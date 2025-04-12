import matplotlib
import matplotlib.pyplot as plt


def create_UV_island_texture(
        width=100, 
        height=100, 
        texture_image_path='single_color_texture_3.png', 
        boundary_width=0.0, 
        boundary_color='black',
        dpi=1500,
        color_alpha=0.65,
        background_alpha=0.8,
        background_img_path='assets/img/fabric_texture.png',
        background_resolution=5,
        preserve_alpha=False
    ):
    """Create texture image from the set of UV boundary loops (e.g. sewing pattern panels). 
        It renders the border of the loops and fills them in with color 
        Params: 
            * boundary_uv_to_draw -- 2D list -- sequence of 2D vertices on each of the boundaries. The order is IMPORTANT. The vertices will be connected 
                by boundary edges sequentially
            * width, height -- the dimentions of the UV map  
            * texture_image_path -- filepath to same a texture image to
            * boundary_width -- width of the boundary outline 
            * dpi -- resolution of the output image
    """
    # Figure size
    fig, ax = plt.subplots()
    fig.set_size_inches(width / 100, height / 100)  # width & height are usually given in cm

    # Colors
    shift = 0.17
    divisor = 9
    cmap = matplotlib.colormaps['twilight']   # copper cool  spring winter twilight  # Using smooth Matplotlib colormaps
    color_sample = [cmap((1 - shift) * id / divisor) for id in range(divisor)]

    # Background -- garment style
    back_crop_scale = background_resolution
    back_img = plt.imread(background_img_path)
    ax.imshow(
        back_img[:int(width * back_crop_scale), :int(height * back_crop_scale), :], 
        extent=[0, width, 0, height], 
        alpha=background_alpha,
        aspect='equal'
    )

    # Draw the UV island boundaries and fill them up
    polygon_x = [0, 0, width, width]  # Rectangle
    polygon_x.append(polygon_x[0])  # Loop
    polygon_y = [0, height, height, 0]  # Rectangle
    polygon_y.append(polygon_y[0])  # Loop

    color = list(color_sample[1])
    color[-1] = color_alpha   # Alpha - transparency for blending with backround

    plt.fill(polygon_x, polygon_y, 
                color=color, 
                edgecolor=boundary_color, linestyle='-', linewidth=boundary_width / 2  # Boundary stylings
    )
        
    ax.set_aspect('equal')

    # Set the axis to be tight
    ax.set_xlim([0, width])
    ax.set_ylim([0, height])

    # Hide the axis
    plt.axis('off')

    # Save image
    plt.savefig(texture_image_path, dpi=dpi, bbox_inches='tight', pad_inches=0, transparent=preserve_alpha)

    # Cleanup
    plt.close()


create_UV_island_texture()
# /is/cluster/fast/sbian/github/GarmentCodeV2/single_color_texture.png
# /is/cluster/fast/sbian/github/LLaVA/runs/try_7b_lr1e_4_v3_garmentcontrol_4h100_nodetail_openai_hood_simulation_garmentcode_eva_pair_crop/vis_new/valid_garment_15__valid_garment_pants_1/valid_garment_wholebody/design.yaml