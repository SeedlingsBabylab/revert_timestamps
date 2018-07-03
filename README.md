# revert_timestamp

given a CHA file with original .lena.cha timestamps, but with subregion comments saying ``` subregion starts at XXX: was YYY```, it will flip all the YYY's back to XXX's


```
$ python revert_to_subregcomm.py input_dir output_dir
```

where input_dir is a folder with cha files, and output_dir is where you want to dump the processed files