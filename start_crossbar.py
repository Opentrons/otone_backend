import multiprocessing


from crossbar.controller.cli import run

if __name__ == '__main__':
    p = multiprocessing.Process(
        target=lambda: run(args=["start"])
    )
    p.start()
    p.join()
