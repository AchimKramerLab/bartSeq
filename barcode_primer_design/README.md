# Primer design and barcode/adapter design

## PrimerSelect Web page
Tool for designing  multiplex primer pairs for the BART-Seq method:
http://icb-bar.helmholtz-muenchen.de

Test files can be found under [example-input-data](https://github.com/theislab/bartSeq/tree/master/barcode_primer_design/example-input-data).


##
## Prerequisites
Bartender software relies on python 3.6+ and depends on the packages in `requirements.txt`.
>You do not have to install those packages, Docker installs them automatically.

## Installing
1. ### Get repository
>Open Terminal, Command Prompt or PowerShell to clone the repository to your computer. You should run all the codes below by one of those.

    ```bash
    git clone https://github.com/theislab/bartSeq.git
    ```

2. ### Download fasta databases
>You do not have to download them using "wget". You can basically click on the links below.
>hg38 is the newer version.

    Download the genomes/transcriptomes you need and move them to the `databases` folder.

    ```bash
    wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
    wget http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.fa.gz
    wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/refMrna.fa.gz
    wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/mrna.fa.gz
    ```

>You have to install BLAST+ to create the databases.

    Create BLAST+ databases for all of them you need.

    ```bash
    makeblastdb -in hg38.fa -dbtype nucl
    makeblastdb -in hg19.fa -dbtype nucl
    makeblastdb -in refMrna.fa -dbtype nucl
    makeblastdb -in mrna.fa -dbtype nucl
    ```

>You do not need to anything about those below.

    Implemented are options to select the following databases with the respective `[filename]`.

    - UCSC Genome hg38 `[hg38.fa]`
    - UCSC Genome hg19 `[hg19.fa]`
    - RefSeq mRNA `[refMrna.fa]`
    - GenBank mRNA `[mrna.fa]`

3. ### Build and run the docker container
>You have to install Docker first. 
>Attention! Building the image may take some time (~30 min)

    Build the docker image and run it. This will start the web service reachable at http://0.0.0.0:5000.

    ```bash
    docker build -t bartender .
    docker run -it --rm -p 5000:5000 bartender
    ```

    Go to http://0.0.0.0:5000 and paste sequences of genes where primers shall be designed for in FASTA format.

    Find example FASTA file and example of primer plus setting files in `example-input-data`.

## Development
>If you get any errors, you can check them by running FLASK_DEBUG.

For development you want to set the environment variable `FLASK_DEBUG` to 1, enabling hot-reloading of your code changes.

### Running the webservice locally
Start the webserver with the following command from the directory this README resides in (Or add that directory to `$PYTHONPATH`)

```bash
FLASK_DEBUG=1 python3 -m bartender.web_frontend
```

### Developing with the docker container
For development we can mount the code as follows by adding software files to the docker container. Build the image as described above. By starting it as follows, the system in the container sees your code changes as they happen.

```bash
docker run \
    -it \
    --rm \
    -v /absolute/path/to/bartSeq/barcode_primer_design:/barcode_primer_design \
    -e FLASK_DEBUG=1 \
    -p 5000:5000 \
    bartender \
    python3 -m bartender/web_frontend
```

## TODO
Currently, the `socketio.emit` in the `web_frontend`’s `__main__.py` does nothing as there’s no page rendered yet.

In order to get a progress bar working, we need to directly render the template and execute the pipeline in a thread, and render the output via JS.

## Authors
* **Steffen Sass** – *Initial work*
* **Nikola Müller** – *Initial documentation*
* **Philipp Angerer** – *Complete overhaul*
* **Merve Büşra Duman** - *Additional notes for complete beginners*
