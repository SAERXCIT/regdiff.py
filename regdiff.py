import sys
import argparse
import asyncio
from aiowinreg.ahive import AIOWinRegHive
from aiowinreg.utils.afile import AFile
from aiowinreg.filestruct.vk import REGTYPE

class RegDiffer():

    def __init__(self, reg_a, reg_b, options):
        self.hive_a = reg_a
        self.hive_b = reg_b
        self.exclude_key_name = options.exclude_name
        self.exclude_key_path = options.exclude_path
        self.truncate = not options.no_truncate

    async def compare_values_in_key(self, base_path):
        current_key_a = await self.hive_a.find_key(base_path)
        list_of_values_a = {} 
        for value_a in await self.hive_a.list_values(current_key_a):
            value_a = value_a.decode()
            value_a_path = base_path + '\\' + value_a
            try:
                value_a_type, value_a_value = await self.hive_a.get_value(value_a, key = current_key_a)
                list_of_values_a |= {value_a: [value_a_type, value_a_value]}
            except UnicodeDecodeError:
                list_of_values_a |= {value_a: [REGTYPE.REG_UNKNOWN, "%ERROR_CANNOT_DECODE_VALUE_A%"]}

        current_key_b = await self.hive_b.find_key(base_path)
        list_of_values_b = {}
        for value_b in await self.hive_b.list_values(current_key_b):
            value_b = value_b.decode()
            value_b_path = base_path + '\\' + value_b
            try:
                value_b_type, value_b_value = await self.hive_b.get_value(value_b, key = current_key_b)
                list_of_values_b |= {value_b: [value_b_type, value_b_value]}
            except UnicodeDecodeError:
                list_of_values_a |= {value_a: [REGTYPE.REG_UNKNOWN, "%ERROR_CANNOT_DECODE_VALUE_A%"]}

        properties_a = set(list_of_values_a.keys())
        properties_b = set(list_of_values_b.keys())

        a_but_not_b = properties_a - properties_b
        b_but_not_a = properties_b - properties_a
        for i in a_but_not_b:
            print("< [{}] Property {}".format(base_path, i))
        for i in b_but_not_a:
            print("> [{}] Property {}".format(base_path, i))

        for i in (properties_a & properties_b):
            type_a, value_a = list_of_values_a[i]
            type_b, value_b = list_of_values_b[i]
            if value_a != value_b:
                if self.truncate and type_a in [REGTYPE.REG_SZ, REGTYPE.REG_EXPAND_SZ, REGTYPE.REG_MULTI_SZ, REGTYPE.REG_BINARY]:
                    value_a_printed = "{}{}".format(value_a[:50], '[%TRUNCATED%]') if len(value_a) > 50 else value_a
                else:
                    value_a_printed = value_a
                if self.truncate and type_b in [REGTYPE.REG_SZ, REGTYPE.REG_EXPAND_SZ, REGTYPE.REG_MULTI_SZ, REGTYPE.REG_BINARY]:
                    value_b_printed = "{}{}".format(value_b[:50], '[%TRUNCATED%]') if len(value_b) > 50 else value_b
                else:
                    value_b_printed = value_b
                print("< [{}] Value {} : {}".format(base_path, i, value_a_printed))
                print("> [{}] Value {} : {}".format(base_path, i, value_b_printed))
        
    async def compare_tree(self, base_path):
        subkeys_a = set(await self.hive_a.enum_key(base_path))
        subkeys_b = set(await self.hive_b.enum_key(base_path))
        a_but_not_b = subkeys_a - subkeys_b
        b_but_not_a = subkeys_b - subkeys_a
        for i in a_but_not_b:
            print("< [{}] Key {}".format(base_path, i))
        for i in b_but_not_a:
            print("> [{}] Key {}".format(base_path, i))
        await self.compare_values_in_key(base_path)
        for i in (subkeys_a & subkeys_b):
            next_path = base_path + "\\" + i if base_path else i
            if i in self.exclude_key_name or next_path in self.exclude_key_path:
                continue
            await self.compare_tree(next_path)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(add_help=True, description="Diffs two registry hives")
    parser.add_argument('regA', action='store', help='1st reg file to diff')
    parser.add_argument('regB', action='store', help='2nd reg file to diff')
    parser.add_argument('--root', '-r', action='store', default='', help='Base path to start the diff from')
    parser.add_argument('--exclude-name', '-en', action='append', metavar='NAME', default=[], help='Exclude keys with name `NAME` from the diff (can be provided multiple times to exclude multiple names)')
    parser.add_argument('--exclude-path', '-ep', action='append', metavar='PATH', default=[], help='Exclude keys at path `PATH` from the diff (can be provided multiple times to exclude multiple paths)')
    parser.add_argument('--no-truncate', '-nt', action='store_true', help='Do not truncate output when displaying long values')
    
    options = parser.parse_args()

    reg_a_handle = AFile(options.regA)
    reg_b_handle = AFile(options.regB)
    hive_a = AIOWinRegHive(reg_a_handle)
    hive_b = AIOWinRegHive(reg_b_handle)

    regdiffer = RegDiffer(hive_a, hive_b, options)
    asyncio.run(regdiffer.compare_tree(options.root))
