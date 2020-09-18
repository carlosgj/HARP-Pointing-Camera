#require 'cosmos/config/config_parser'
require 'cosmos/interfaces/protocols/protocol'
require 'thread'

module Cosmos
  # 
  class LengthCheck < Protocol
    def initialize()
      super(allow_empty_data)
	end

    def read_data(data)
	  return super(data) if (data.length <= 0)
	  length = BinaryAccessor.read(0,8,:UINT,data,'BIG_ENDIAN')
	  if data.length != (length + 1)
		Logger.error "Incorrect length field: #{length}. Actual packet size: #{data.length-1}."
		return ""
	  end
      return data
    end
	
	def write_packet(packet)
        length = packet.length
        packet.write('LENGTH', length-1)

      return packet
    end
	
  end
end
