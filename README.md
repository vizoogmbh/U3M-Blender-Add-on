# **U3M Blender Add-on**

## **About:** 
The U3M Blender Add-on allows you to import/export any [Unified 3D Material](https://github.com/vizoogmbh/u3m) to/from [Blender](https://www.blender.org/).<br/> The included 'U3M Editor' gives you full control over modifying the accurately imported texture maps and parameters of your U3M. 
The Add-on supports all current versions (v1.0 & v1.1) of the U3M fileformat (*.u3m).<br/><br/> 
This version supports Blender 4.2 LTS. Due to breaking changes, it is not compatible with older versions. If you want to use it with Blender 2 or 3, use an add-on version lower than 1.2.x.

### Installing & Enabling the Add-on:
To install the add-on, download the latest release zip from the GitHub Releases section of this repository, where it can be found attached to the corresponding version tag.

In Blender, navigate to:

*Edit > Preferences > Add-ons > Install*

Select the downloaded zip file and install it. Once installed, enable the add-on by ticking the checkbox in the add-ons list.</br><br/>
More information can be found in the [Vizoo Customer Portal](https://customers.vizoo3d.com/wp-content/uploads/2021/05/U3MBlenderAdd-on_documentation.pdf)</br>

### Importing U3Ms:
After enabling the Add-on you can import any U3M to your active 3D object (meshes only) via:<br/>

> *File>Import>Unified 3D Material (.u3m)*<br/>  

Note: *The scale of the material will be automatically determined by the size of your 3D objects UV map dimensions (works best with rectangular uv-maps). To change the scaling of your material manually use the scaling-slider in the U3M Tools section of the Blender Toolbar.* 

### Modifying U3Ms:
You can modify all of your U3Ms front- and back side texture maps and parameters with the 'U3M Editor' of this add-on. 

Note: *"Side"-side from U3M v1.1 is currently not supported.*
### Exporting U3Ms:
After importing a U3M, you can modify and export it again via:<br/> 

> *File>Export>Unified 3D Material (.u3m)*<br/>

Note: *All changes applied to the U3M via the 'U3M Editor' can be exported. This does not include any additional nodes added manually to the shader.*

## **Copyright & License**
Copyright 2020-2025 Vizoo GmbH<br/>
[GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.txt)<br/>

## **Contact** 
support@vizoo3d.com<br/>
+49 89 379 176 47