#require 'cosmos/config/config_parser'
require 'cosmos/interfaces/protocols/protocol'
require 'thread'

module Cosmos
  # 
  class ByteStuff < Protocol

    # @param write_item_name [String/nil] Item to fill with calculated CRC value for outgoing packets (nil = don't fill)
    # @param strip_crc [Boolean] Whether or not to remove the CRC from incoming packets
    # @param bad_strategy [ERROR/DISCONNECT] How to handle CRC errors on incoming packets.  ERROR = Just log the error, DISCONNECT = Disconnect interface
    # @param bit_offset [Integer] Bit offset of the CRC in the data.  Can be negative to indicate distance from end of packet
    # @param bit_size [Integer] Bit size of the CRC - Must be 16, 32, or 64
    # @param endianness [BIG_ENDIAN/LITTLE_ENDIAN] Endianness of the CRC
    # @param poly [Integer] Polynomial to use when calculating the CRC
    # @param seed [Integer] Seed value to start the calculation
    # @param xor [Boolean] Whether to XOR the CRC result with 0xFFFF
    # @param reflect [Boolean] Whether to bit reverse each byte of data before calculating the CRC
    # @param allow_empty_data [true/false/nil] See Protocol#initialize
    def initialize()
      super(allow_empty_data)
	end
    def read_data(data)
      return super(data) if (data.length <= 0)
      return data
    end

    def write_packet(packet)
      packet
    end

    def write_data(data)
      data
    end
  end
end
