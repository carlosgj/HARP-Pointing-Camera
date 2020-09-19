#require 'cosmos/config/config_parser'
require 'cosmos/interfaces/protocols/protocol'
require 'thread'

module Cosmos
  # 
  class ByteStuff < Protocol
    def initialize()
      super(allow_empty_data)
	end

    def read_data(data)
	  return super(data) if (data.length <= 0)
	  Logger.info "ByteStuff Packet!"
	  Logger.info data
      return data
    end
  end
end
