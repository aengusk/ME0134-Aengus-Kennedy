from Husky.huskylensPythonLibrary import HuskyLensLibrary as Husky

husky = Husky('I2C')


state = husky.command_request_arrows()