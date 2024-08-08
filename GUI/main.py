import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from astropy.io import fits
import astropy_healpix as ah
import astropy.units as u
from astropy.table import QTable
from PIL import Image, ImageTk

class LogoWindow:
    def __init__(self, logo_path):
        self.logo_path = r"C:\Users\Shubhankar Kulkarni\Downloads\skymap logo.jpg"

        self.logo_root = tk.Tk()
        self.logo_root.geometry("300x200")
        self.logo_root.title("Skymap Viewer")

        self.logo = Image.open(self.logo_path)
        self.logo = ImageTk.PhotoImage(self.logo)

        self.logo_label = tk.Label(self.logo_root, image=self.logo)
        self.logo_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.logo_root.after(3000, self.logo_root.destroy)
        self.logo_root.mainloop()

class SkymapVisualizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Skymap Visualizer")
        self.geometry("800x600")

        self.current_cmap = 'viridis'

        self.bg_image = Image.open("C:/Users/Shubhankar Kulkarni/Downloads/scr00027.png")
        self.bg_image = self.bg_image.resize((800, 600), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas to display the background image
        self.canvas = tk.Canvas(self, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Create a menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Create view menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="2D Mollweide", command=self.view_mollweide)
        view_menu.add_command(label="2D Scatter", command=self.view_scatter)
        view_menu.add_command(label="3D Scatter", command=self.view_3dscatter)
        view_menu.add_command(label="2D Mollweide Flat", command=self.view_mollweide_flat)
        view_menu.add_command(label="50% & 90% Confidence Regions", command=self.view_90p50p)
        view_menu.add_command(label="Healpix Mollweide", command=self.view_healpix_mollweide)
        view_menu.add_command(label="Mollweide Multiscatter", command=self.view_mollweidemultiscatter)

        color_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Color", menu=color_menu)
        colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'twilight', 'cool', 'hot', 'rainbow']
        for cmap in colormaps:
            color_menu.add_command(label=cmap, command=lambda cmap=cmap: self.set_colormap(cmap))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View Help", command=self.show_help)

        # Add About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About Skymap Visualizer", command=self.show_about)



        # Create a frame for the plot
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def show_help(self):
        help_text = (
            "This is the Skymap Visualizer Application.\n"
            "Here are some steps to use the application:\n"
            "1. Load a FITS file using the 'File' menu.\n"
            "2. Select different visualization modes.\n"
            "3. Customize the colormap from the options provided.\n"
            "4. For detailed analysis, use the 90% Confidence Region view.\n\n"
            "For further assistance, contact support.\n"
            "Shubhankar Kulkarni (ks2197@srmist.edu.in\n"
            "Xiyuan Li (xli2522@uwo.ca)\n"
        )
        messagebox.showinfo("Help", help_text)

    def show_about(self):
        about_text = (
            "Skymap Visualizer v1.0\n\n"
            "Developed by Prof. Shree Ram Valluri's GW Research Group at Western Univerity, Ontario, Canada.\n"
            "This application allows you to visualize skymaps from FITS files with various projection modes and contour regions.\n\n"
            "For more information, check the documentation."
        )
        messagebox.showinfo("About", about_text)

    def set_colormap(self, cmap):
        self.current_cmap = cmap
        messagebox.showinfo("Colormap Set", f"Colormap set to {cmap}")

    def load_fits_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("FITS files", "*.fits"), ("All files", "*.*")])
        if not file_path:
            messagebox.showerror("Error", "No file selected.")
            return None

        try:
            with fits.open(file_path) as hdul:
                skymap = QTable(hdul[1].data)  # Assuming data is in the first HDU
                self.current_file_path = file_path
                return skymap, hdul
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load FITS file: {e}")
            return None, None

    def extract_header_info(self, hdul):
        keywords = ['OBJECT', 'REFERENC', 'INSTRUME', 'DATE-OBS', 'MJD-OBS']
        info = {key: 'N/A' for key in keywords}

        for hdu in hdul:
            for key in keywords:
                if key in hdu.header and info[key] == 'N/A':
                    info[key] = hdu.header[key]

        info_text = (
            f"OBJECT: {info['OBJECT']}\n"
            f"REFERENCE: {info['REFERENC']}\n"
            f"INSTRUMENT: {info['INSTRUME']}\n"
            f"DATE-OBS: {info['DATE-OBS']}\n"
            f"MJD-OBS: {info['MJD-OBS']}"
        )
        return info_text

    def plot_with_header_info(self, fig, ax, info_text):
        """Add a box with header info to the plot."""
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

    def view_mollweide(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')

            lon_array = np.array(lon) - np.pi
            lat_array = np.array(lat)

            plt.figure(figsize=(12, 6))
            ax = plt.subplot(111, projection='mollweide')
            sc = ax.scatter(lon_array, lat_array, s=1, c=skymap['PROBDENSITY'].value, cmap=self.current_cmap)
            ax.set_title('Mollweide Projection')
            ax.grid(True)
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label('Probability Density')
            plt.tight_layout()

            info_text = self.extract_header_info(hdul)
            self.plot_with_header_info(plt.gcf(), ax, info_text)

            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize Mollweide projection: {e}")

    def view_scatter(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')

            plt.figure(figsize=(12, 6))
            plt.scatter(lon, lat, s=1, c=skymap['PROBDENSITY'].value, cmap=self.current_cmap)
            plt.title('2D Scatter Plot')
            plt.xlabel('Longitude (radians)')
            plt.ylabel('Latitude (radians)')
            plt.colorbar(label='Probability Density')
            plt.grid(True)
            plt.tight_layout()

            info_text = self.extract_header_info(hdul)
            self.plot_with_header_info(plt.gcf(), plt.gca(), info_text)

            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize 2D scatter plot: {e}")

    def view_3dscatter(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')

            x = np.cos(lon) * np.cos(lat)
            y = np.sin(lon) * np.cos(lat)
            z = np.sin(lat)

            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(111, projection='3d')
            sc = ax.scatter(x, y, z, s=1, c=skymap['PROBDENSITY'].value, cmap=self.current_cmap)
            ax.set_title('3D Scatter Plot')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label('Probability Density')
            plt.tight_layout()

            info_text = self.extract_header_info(hdul)
            # Use text method correctly for 3D axes
            ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                      verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize 3D scatter plot: {e}")

    def view_mollweide_flat(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            # Filter out points with probability density less than 10%
            skymap = skymap[skymap['PROBDENSITY'] > 0.01]

            # Extract relevant data
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')

            # Define the color for 0% density in the 'viridis' colormap
            cmap = plt.get_cmap(self.current_cmap)
            norm = plt.Normalize(vmin=0, vmax=1)
            zero_density_color = cmap(norm(0))  # Color for 0% density

            plt.figure(figsize=(12, 6))
            ax = plt.subplot(111, projection='mollweide')

            # Set the background color to the color representing 0% density
            ax.set_facecolor(zero_density_color)

            # Plot points with density between 10% and 100%
            scatter = ax.scatter(np.array(lon) - np.pi, np.array(lat), s=1, c=skymap['PROBDENSITY'].value,
                                 cmap=self.current_cmap, vmin=0.1, vmax=1.0)

            plt.title('Mollweide Projection Flat')
            plt.grid(True)
            plt.colorbar(scatter, label='Probability Density')
            plt.tight_layout()

            # Display header information
            info_text = self.extract_header_info(hdul)
            self.plot_with_header_info(plt.gcf(), plt.gca(), info_text)

            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize Mollweide projection flat: {e}")

    def view_90p50p(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            pixel_area = ah.nside_to_pixel_area(nside).to(
                u.steradian).value  # Convert to steradians and then to a dimensionless value
            prob = pixel_area * skymap['PROBDENSITY'].value
            cumprob = np.cumsum(prob)

            i_50 = cumprob.searchsorted(0.5)
            i_90 = cumprob.searchsorted(0.9)

            area_50 = np.sum(pixel_area[:i_50]) * u.steradian
            area_90 = np.sum(pixel_area[:i_90]) * u.steradian

            skymap_50 = skymap[:i_50]
            skymap_90 = skymap[:i_90]

            skymap_50.sort('UNIQ')
            skymap_90.sort('UNIQ')

            level50P, ipix50P = ah.uniq_to_level_ipix(skymap_50['UNIQ'])
            nside50P = ah.level_to_nside(level50P)
            lon50P, lat50P = ah.healpix_to_lonlat(ipix50P, nside50P, order='nested')

            level90P, ipix90P = ah.uniq_to_level_ipix(skymap_90['UNIQ'])
            nside90P = ah.level_to_nside(level90P)
            lon90P, lat90P = ah.healpix_to_lonlat(ipix90P, nside90P, order='nested')

            lon_array50, lat_array50 = np.array(lon50P) - np.pi, np.array(lat50P)
            lon_array90, lat_array90 = np.array(lon90P) - np.pi, np.array(lat90P)

            plt.figure(figsize=(12, 6))
            ax = plt.subplot(111, projection='mollweide')
            sc = ax.scatter(lon_array50, lat_array50, s=1, c=skymap_50['PROBDENSITY'].value, cmap=self.current_cmap,
                            label='50% Confidence')

            ax.scatter(lon_array90, lat_array90, s=1, c=skymap_90['PROBDENSITY'].value, cmap=self.current_cmap,
                       label='90% Confidence')

            ax.set_title('Mollweide Projection: Overlapping Confidence Regions\n', loc='center')
            ax.grid(True)

            ax.annotate('50%', xy=(
                lon_array50[np.argmax(skymap_50['PROBDENSITY'])], lat_array50[np.argmax(skymap_50['PROBDENSITY'])]),
                        xytext=(lon_array50[np.argmax(skymap_50['PROBDENSITY'])] + np.pi / 30,
                                lat_array50[np.argmax(skymap_50['PROBDENSITY'])] + np.pi / 30),
                        arrowprops=dict(facecolor='black', arrowstyle='->'),
                        fontsize=10, horizontalalignment='left', verticalalignment='bottom')

            ax.annotate('90%', xy=(
                lon_array90[np.argmax(skymap_90['PROBDENSITY'])], lat_array90[np.argmax(skymap_90['PROBDENSITY'])]),
                        xytext=(lon_array90[np.argmax(skymap_90['PROBDENSITY'])] + np.pi / 30,
                                lat_array90[np.argmax(skymap_90['PROBDENSITY'])] + np.pi / 30),
                        arrowprops=dict(facecolor='black', arrowstyle='->'),
                        fontsize=10, horizontalalignment='left', verticalalignment='bottom')

            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label('Probability Density')

            ax.legend()

            textstr = f'Area of 50% confidence region: {area_50.to(u.deg ** 2).value:.3f} deg^2\nArea of 90% confidence region: {area_90.to(u.deg ** 2).value:.3f} deg^2'
            props = dict(boxstyle='round', facecolor='white', alpha=0.5)
            ax.text(0.5, -0.15, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
                    horizontalalignment='center', bbox=props)

            info_text = self.extract_header_info(hdul)
            self.plot_with_header_info(plt.gcf(), plt.gca(), info_text)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize confidence regions: {e}")

    def view_healpix_mollweide(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            skymap.sort('PROBDENSITY', reverse=True)
            level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')
            prob_density = skymap['PROBDENSITY'].value

            # Ensure lon and pi have compatible units before subtraction
            lon_shifted = lon.to_value(u.rad) - np.pi
            lon_shifted = lon_shifted * u.rad

            fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': 'mollweide'})
            ax.set_facecolor('LightCyan')
            sc = ax.scatter(lon_shifted.to_value(u.rad), lat.to_value(u.rad), c=prob_density, cmap=self.current_cmap, s=1,
                            alpha=0.8)

            # Highlighting the most probable location
            max_prob_index = np.argmax(prob_density)
            max_lon = lon_shifted[max_prob_index].to_value(u.rad)
            max_lat = lat[max_prob_index].to_value(u.rad)
            ax.scatter(max_lon, max_lat, color='red', marker='*', s=100, label='Most Probable Location')

            ax.set_title('Healpix Mollweide Projection')
            fig.colorbar(sc, ax=ax, orientation='vertical')
            ax.grid(True)
            ax.legend()  # Show legend for the most probable location marker

            info_text = self.extract_header_info(hdul)
            self.plot_with_header_info(fig, ax, info_text)

            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize Healpix Mollweide projection: {e}")

    def view_mollweidemultiscatter(self):
        skymap, hdul = self.load_fits_file()
        if skymap is None:
            return

        try:
            # Extract header information for display
            info_text = self.extract_header_info(hdul)

            # Retrieve necessary data from skymap
            prob_density = skymap['PROBDENSITY']  # Use the correct key
            uniq = skymap['UNIQ']  # Use the correct key

            # Create the Mollweide projection plot
            fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': 'mollweide'})
            ax.set_facecolor('LightCyan')

            # Convert Healpix coordinates to longitude and latitude
            level, ipix = ah.uniq_to_level_ipix(uniq)
            nside = ah.level_to_nside(level)
            lon, lat = ah.healpix_to_lonlat(ipix, nside, order='nested')
            lon_shifted = lon - np.pi * u.rad

            # Scatter plot with confidence region
            cred_levelMap = ax.scatter(lon_shifted.to_value(u.rad), lat.to_value(u.rad), c=prob_density, marker='s',
                                       s=3, cmap=self.current_cmap)
            ax.set_title('Mollweide Multiorder Test')
            fig.colorbar(cred_levelMap, ax=ax, label='Probability Density')
            ax.grid(True)

            # Display plot with header info
            self.plot_with_header_info(fig, ax, info_text)

            plt.show()
        except KeyError as e:
            messagebox.showerror("Error", f"Missing key in skymap data: {e}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize Mollweide multiscatter projection: {e}")


if __name__ == "__main__":
    logo_window = LogoWindow(r"C:\Users\Shubhankar Kulkarni\Downloads\skymap logo.jpg")
    app = SkymapVisualizerApp()
    app.mainloop()
