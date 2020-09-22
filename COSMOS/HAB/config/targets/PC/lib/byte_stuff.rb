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
      $i = 0
      $newdata = ""
      while $i < data.length do
        if data[$i].ord == 0x7d
            $i += 1
            $newdata << (data[$i].ord ^ 0b00100000).chr
        else
            $newdata << data[$i]
        end
        $i += 1
      end
      return $newdata
    end
    
    
    def write_data(data)
        $i = 0
        $newdata = ""
        while $i < data.length do
            if data[$i].ord == 0x7d or data[$i].ord == 0x7d or data[$i].ord == 0x7d
                $newdata << 0x7d.chr
                $newdata << (data[$i].ord ^ 0b00100000).chr
            else
                $newdata << data[$i]
            end
            $i += 1
        end
        return $newdata
    end
    
  end
end
