import subprocess



def _sys_argv_from_args(args: Iterable[str]) -> tuple[str, subprocess.CompletedProcess] :
    

    result = subprocess.run(f'python -X utf8 args.py {" ".join(args)}'
                           ,shell = True
                           ,stderr=subprocess.STDOUT
                           ,stdout = subprocess.PIPE
                           )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result