## S2GConverter

### Description 

Python utility for converting 3D models from the Source engine to the GoldSource engine. This tool supports the conversion of models with any number of polygons and animations, making it highly versatile for modding and game development purposes. Key features include: 

- Unlimited polygon count support: Seamlessly convert models regardless of complexity or polygon count.
- Animation preservation: Full support for importing and converting animated models.  
- Pseudo-normal map generation: Automatically generates pseudo-normal maps by combining the original texture with its derived normal map data, enhancing surface detail in GoldSource-compatible formats.  
- Texture fusion: Creates enriched textures by merging diffuse textures with normal map information, improving visual fidelity within the limitations of the GoldSource rendering pipeline.
     
This utility bridges the gap between modern Source-based assets and the legacy GoldSource engine, enabling developers and modders to reuse advanced models in older games with enhanced visual quality. 

### Installation

1) You should have Python 3 installed
2) Install the requirements using command

```
pip install -r requirements.txt
```

3) Not the utility is ready to be used

### Usage 

1) Before usage you should put model files with extensions ```.vtf```, ```.vmt```, ```.mdl```, and ```.vvd``` to one folder, like shown on image.

<img width="701" height="145" alt="{43287408-2C24-4080-8AC8-828A787B6BEA}" src="https://github.com/user-attachments/assets/8e89d0cf-34ef-422f-90b1-f0e813e0943c" />

2) Run command

```
python S2GConverter.py -i "path/to/your/model.mdl" [--generate_pnmaps | --no-generate_pnmaps]
```

The following command line argumetns are available

| Argument | Type | Default | Description |
|--------|------|---------|-------------|
| `-i`, `--input` | `str` (required) | — | Path to the `.mdl` file you want to convert. Must include all associated Source engine assets in the same directory. |
| `--generate_pnmaps`, `--no-generate_pnmaps` | `boolean` | `True` | Enables or disables **pseudo-normal map generation**. When enabled, the tool enhances texture detail by combining the base texture with its corresponding normal map (from the `.vmt`'s `bumpmap` parameter), simulating better lighting on GoldSource’s flat shading. |

You will find the converted model with name ```{source_model_name}_goldsource.mdl``` in the folder with the source model files.

### Pseudo normal maps

Some older game engines like GoldSource do not support certain technologies. These technologies may include Normal Mapping - a texture mapping technique used for faking the lighting of bumps and dents. S2GConverter uses the existing normal map and  process the texture, so you can get something close to the bump mapping result.

<img width="1206" height="588" alt="example_2" src="https://github.com/user-attachments/assets/27d92fb4-3754-41fe-ae26-cefcd522a1a6" />

### Existing restrictions

There are two situations yet, when the model can't be converted. These are:

- The model contains sequences larger, than 64Kb.
- The model has 129 and more bones.

### Results examples

<img width="1984" height="1844" alt="examples" src="https://github.com/user-attachments/assets/eeffada9-ca48-420d-80aa-fc056a69490b" />

### Credits and Links

1) [PrimeXT - Modernized toolkit for Xash3D FWGS engine](https://github.com/SNMetamorph/PrimeXT)
2) [VTFLib](https://nemstools.github.io/subpages/Comments/VTFEdit_v1.3.3_Full-page2.html#p238)
3) Sources of models demonstrated here
    1) [Serious Sam 2 SWEPS](https://steamcommunity.com/sharedfiles/filedetails/?id=503138986)
    2) [DOOM Eternal NPCs]https://steamcommunity.com/sharedfiles/filedetails/?id=2295322924
    3) [Dark Souls NPCs reworked]https://steamcommunity.com/sharedfiles/filedetails/?id=1254104064  
