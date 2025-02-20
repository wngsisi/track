# Python脚本，用于输入一串6个十六进制数，以空格分隔，计算它们的和然后对100取余，并转换为16进制

# 函数：将十六进制字符串转换为十进制数
def hex_to_decimal(hex_str):
    try:
        # 将十六进制字符串转换为十进制数
        decimal_value = int(hex_str, 16)
        return decimal_value
    except ValueError:
        print(f"Error: '{hex_str}' is not a valid hexadecimal number.")
        return None

# 获取用户输入的十六进制数串
hex_input = input("Enter a sequence of 6 hexadecimal numbers separated by spaces: ")

# 分割输入的字符串，获取每个十六进制数
hex_numbers = hex_input.split()

# 初始化总和变量
total_sum = 0

# 将每个十六进制数转换为十进制并累加
for hex_num in hex_numbers:
    decimal_value = hex_to_decimal(hex_num)
    if decimal_value is not None:
        total_sum += decimal_value
    else:
        # 如果转换失败，提示用户并退出脚本
        print("One or more of the entered numbers is not a valid hexadecimal. Exiting.")
        exit()

# 对总和进行100取余
mod_result = total_sum % 100

# 将结果转换为十六进制，并保持至少两位数（如果需要的话）
hex_result = format(mod_result, '02x')

# 打印结果
print(f"The sum of the hexadecimal numbers mod 100 is: {hex_result}")
