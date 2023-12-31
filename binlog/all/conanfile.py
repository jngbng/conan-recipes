from conan import ConanFile
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class BinlogRecipe(ConanFile):
    name = "binlog"
    package_type = "library"
    license = "Apache-2.0"
    url = "https://github.com/morganstanley/binlog"
    description = "A high performance C++ log library, producing structured binary logs"
    topics = ("logger", "logging", "high performance", "header-only")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "build_bread": [True, False],
        "build_brecovery": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "build_bread": True,
        "build_brecovery": True,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("build_bread")
            self.options.rm_safe("build_brecovery")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["BINLOG_BUILD_EXAMPLES"] = False
            tc.variables["BINLOG_BUILD_UNIT_TESTS"] = False
            tc.variables["BINLOG_BUILD_INTEGRATION_TESTS"] = False
            tc.variables["BINLOG_BUILD_BREAD"] = self.options.build_bread
            tc.variables["BINLOG_BUILD_BRECOVERY"] = self.options.build_brecovery
            tc.generate()
        # No dependencies
        # deps = CMakeDeps(self)
        # deps.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self,
                 src=os.path.join(self.source_folder, "include"),
                 pattern="*.hpp", dst=os.path.join(self.package_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            # rmdir(self, os.path.join(self.package_folder, "share"))
            # rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            # rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
            # rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.libs = []
            self.cpp_info.libdirs = []
            self.cpp_info.bindirs = []
            self.cpp_info.set_property("cmake_target_name", "binlog::binlog_header_only")
        else:
            self.cpp_info.libs = ["binlog"]

        self.cpp_info.set_property("cmake_file_name", "binlog")

        # # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # self.cpp_info.filenames["cmake_find_package"] = "BINLOG"
        # self.cpp_info.filenames["cmake_find_package_multi"] = "binlog"
        # self.cpp_info.names["cmake_find_package"] = "BINLOG"
        # self.cpp_info.names["cmake_find_package_multi"] = "binlog"
