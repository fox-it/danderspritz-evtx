# danderspritz-evtx
Parse evtx files and detect use of the DanderSpritz `eventlogedit` module

* Blog post here: https://blog.fox-it.com/2017/12/08/detection-and-recovery-of-nsas-covered-up-tracks/
* Precompiled Windows binary here: https://github.com/fox-it/danderspritz-evtx/releases

Example evtx files can be found in [examples](https://github.com/fox-it/danderspritz-evts/examples/)

## Usage

```
$ ./danderspritz_evtx.py -h
usage: danderspritz_evtx.py [-h] -i INPUT_PATH [-o OUTPUT_PATH]
                            [-e EXPORT_PATH]

danderspritz_evtx.py - Parse evtx files and detect the use of the danderspritz
module that deletes evtx entries

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input INPUT_PATH
                        Path to evtx file
  -o OUTPUT_PATH, --output OUTPUT_PATH
                        Path to corrected evtx file
  -e EXPORT_PATH, --export EXPORT_PATH
                        Path to location to store exported xml records
```

## Example output

```
$ ./danderspritz_evtx.py -i Security.evtx -o Security_fixed.evtx -e Security_export.xml
Reading records from Security.evtx...
Found a deleted record within record number 2112 at offset 0x1EA0
Found a deleted record within record number 2112 at offset 0x1CD8
Found a deleted record within record number 2112 at offset 0x1B30
Found a deleted record within record number 2112 at offset 0x1240
Found a deleted record within record number 2112 at offset 0x0618
Found a deleted record within record number 2112 at offset 0x01E8
Found a deleted record within record number 2113 at offset 0x08C0
```
