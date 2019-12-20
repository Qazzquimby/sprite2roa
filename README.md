# sprite2roa
A tool for processing sprites for Rivals of Aether modding.

Any game's sprites go in, some quick Rivals of Aether sprites come out.
![_8](https://user-images.githubusercontent.com/12368310/71284520-c6844a80-2317-11ea-9ed0-8ad2998d1112.png)

It's meant to be a good starting point for porting existing characters over, and cut down on the development time for sprites.

## Existing content
Already processed sprites can be found [here](https://mega.nz/#F!px8w3KTQ!HvGsOg6-LB0HdkI1UomC_w)
If you have a substantial sprite repository to add, please contact me  to add it.

## Usage
Though all the code is released available, only the dist directory is required for use.

Create an `input` directory inside dist, with a structure matching the example folders in the root input folder.
None of the config files are required, but the `avg_char_height` value must be set in either a config or a cmd argument.

Example valid folder configurations are:

`dist/input/ultimate/Bowser/(many animation .gif files)` # With one_frame_per_file set false in a config or cmd argument.
`dist/input/skullgirls/filia/animation_name/(many files representing individual frames)` #With one_frame_per_file set true.

Then run sprite2roa.exe. 
By default it will process each game and character in the input directory using the config files found inside.
By running it on a command line, itIt can be set to process only one game, or only one character from that game, and override the existing config with command line arguments.

An example call argument is given in the file `double_size.bat`, which simply doubles the resolution of all files in `input`.

Full call arguments are below, and can be viewed by adding -h to the command.
```
Usage:
    sprite2roa.exe
    sprite2roa.exe [<game_name> [<char_name>]] [options]
    sprite2roa.exe -h|--help
    sprite2roa.exe -v|--version

Options:
    # <game_name>     The game to process, matching the name of a directory in the input folder.
    # <char_name>     The character to process, matching the name of a directory in a game's folder.
    # Eg. sprite2roa.py skullgirls filia (reads from the directory input/skullgirls/filia)
    -h --help       Show this screen.
    -v --version    Show version.

    --avg_char_height <height>
    # The average character height in the source images, in pixels.
    # Required unless specified in config.ini
    # Used to appropriately scale character's to Rivals of Aether average height of ~30 px.
    # Larger value produces smaller sprites.
    # Eg. 230

    --one_frame_per_file
    # When this is *not* set, it is assumed that each file represents an animation (either a sprite sheet or a gif)
    # When this is set, it is assumed that each directory of files represents an animation,
    #    with each file in the directory being a frame in that animation.

    --should_outline
    # When this is set, a single pixel outline is added to the output sprites. Recommended.

    --background_color <color>
    # Replaces the given rgb value with transparency.
    # Must have three values in the range [0, 255]
    # Eg. 64 64 64

    --saturation <amount>
    # Scales the sprites color saturation by the given amount.
    # Eg. 1.5
```

## Contact
If something is broken or confusing, you can raise an issue in github or contact me at Qazzquimby#0073 on discord.
