require_relative '../client'


describe Client do
  let(:udp_client) { double 'udp_client' }
  let(:joystick) { double 'joystick' }

  before :each do
    allow(UDPClient).to receive(:new).and_return udp_client
    allow(Joystick).to receive(:new).and_return joystick
    allow(joystick).to receive :update
    allow(joystick).to receive(:axis).and_return({})
    allow(udp_client).to receive :write
  end

  describe :initialize do
    it 'should connect to the robot via UDP' do
      expect(UDPClient).to receive :new
      Client.new
    end

    it 'should initialize the joystick' do
      expect(Joystick).to receive :new
      Client.new
    end
  end

  describe :update do
    it 'should update the joystick' do
      expect(joystick).to receive :update
      Client.new.update
    end

    it 'should send the axes values' do
      expect(udp_client).to receive(:write).with '0,0'
      Client.new.update
    end

    it 'should get the axes values from the joystick' do
      allow(joystick).to receive(:axis).and_return({1 => 42, 4 => -180})
      expect(udp_client).to receive(:write).with '42,-180'
      Client.new.update
    end
  end
end
