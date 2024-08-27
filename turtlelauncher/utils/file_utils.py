from loguru import logger
import os

def has_directory_permissions(directory):
        logger.info(f"Checking permissions for directory: {directory}")
        try:
            # Check read permission
            logger.debug("Checking read permission...")
            os.listdir(directory)
            logger.debug("Read permission check passed")
            
            # Check write permission
            logger.debug("Checking write permission...")
            test_file = os.path.join(directory, 'test_write_permission.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.debug("Write permission check passed")
            
            # Check execute permission
            logger.debug("Checking execute permission...")
            original_dir = os.getcwd()
            os.chdir(directory)
            os.chdir(original_dir)  # Change back to original directory
            logger.debug("Execute permission check passed")
            
            logger.info(f"All permission checks passed for directory: {directory}")
            return True
        except PermissionError as pe:
            logger.error(f"Permission error encountered: {pe}")
            return False
        except OSError as ose:
            logger.error(f"OS error encountered: {ose}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during permission check: {e}")
            return False