/*
 * Win-NetSight 核心采集器 (Windows 版)
 * 使用 Windows IP Helper API 实时监控网络连接和流量。
 */

#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>
#include <thread>
#include <chrono>
#include <map>

#include <winsock2.h>
#include <iphlpapi.h>
#include <ws2tcpip.h>

#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")

// 辅助函数：将 IP 地址转换为字符串
std::string ip_to_string(DWORD ip_addr) {
    char buffer[INET_ADDRSTRLEN];
    struct in_addr addr;
    addr.S_un.S_addr = ip_addr;
    InetNtopA(AF_INET, &addr, buffer, sizeof(buffer));
    return buffer;
}

// 辅助函数：将端口号转换为字符串
std::string port_to_string(WORD port) {
    return std::to_string(ntohs(port));
}

int main() {
    // 初始化 Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed.\n";
        return 1;
    }

    // 预热输出，确保 Python 端能正确解析初始 JSON
    std::cout << "{\"connections\": []}" << std::endl;

    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));

        std::stringstream json_output;
        json_output << "{\"connections\": [";

        // 获取 TCP 连接信息
        PMIB_TCPTABLE_OWNER_PID pTcpTable;
        DWORD dwSize = 0;
        if (GetExtendedTcpTable(NULL, &dwSize, FALSE, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0) == ERROR_INSUFFICIENT_BUFFER) {
            pTcpTable = (PMIB_TCPTABLE_OWNER_PID) malloc(dwSize);
            if (GetExtendedTcpTable(pTcpTable, &dwSize, FALSE, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0) == NO_ERROR) {
                for (DWORD i = 0; i < pTcpTable->dwNumEntries; i++) {
                    if (i > 0) json_output << ",";
                    json_output << "{"
                                << "\"protocol\": \"TCP\","
                                << "\"local_addr\": \"" << ip_to_string(pTcpTable->table[i].dwLocalAddr) << "\","
                                << "\"local_port\": \"" << port_to_string(pTcpTable->table[i].dwLocalPort) << "\","
                                << "\"remote_addr\": \"" << ip_to_string(pTcpTable->table[i].dwRemoteAddr) << "\","
                                << "\"remote_port\": \"" << port_to_string(pTcpTable->table[i].dwRemotePort) << "\","
                                << "\"pid\": " << pTcpTable->table[i].dwOwningPid << ","
                                << "\"state\": " << pTcpTable->table[i].dwState
                                << "}";
                }
            }
            free(pTcpTable);
        }

        // 获取 UDP 连接信息 (简化处理，只获取端口)
        PMIB_UDPTABLE_OWNER_PID pUdpTable;
        dwSize = 0;
        if (GetExtendedUdpTable(NULL, &dwSize, FALSE, AF_INET, UDP_TABLE_OWNER_PID, 0) == ERROR_INSUFFICIENT_BUFFER) {
            pUdpTable = (PMIB_UDPTABLE_OWNER_PID) malloc(dwSize);
            if (GetExtendedUdpTable(pUdpTable, &dwSize, FALSE, AF_INET, UDP_TABLE_OWNER_PID, 0) == NO_ERROR) {
                for (DWORD i = 0; i < pUdpTable->dwNumEntries; i++) {
                    if (pTcpTable && pTcpTable->dwNumEntries > 0 || i > 0) json_output << ","; // 确保 JSON 格式正确
                    json_output << "{"
                                << "\"protocol\": \"UDP\","
                                << "\"local_addr\": \"" << ip_to_string(pUdpTable->table[i].dwLocalAddr) << "\","
                                << "\"local_port\": \"" << port_to_string(pUdpTable->table[i].dwLocalPort) << "\","
                                << "\"remote_addr\": \"::\","
                                << "\"remote_port\": \"0\","
                                << "\"pid\": " << pUdpTable->table[i].dwOwningPid << ","
                                << "\"state\": 0"
                                << "}";
                }
            }
            free(pUdpTable);
        }

        json_output << "]}";
        std::cout << json_output.str() << std::endl;
    }

    WSACleanup();
    return 0;
}
